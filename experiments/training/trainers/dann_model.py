"""
Domain-Adversarial Neural Network (DANN) implementation.

Includes FeatureExtractor, LabelClassifier, DomainClassifier, DANN, and DANNTrainer.
"""

import copy
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from .gradient_reversal import GradientReversalLayer, lambda_scheduler

logger = logging.getLogger(__name__)

class FeatureExtractor(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        super().__init__()
        layers = []
        current_dim = input_dim
        for h_dim in hidden_dims:
            layers.extend([
                nn.Linear(current_dim, h_dim),
                nn.BatchNorm1d(h_dim),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3)
            ])
            current_dim = h_dim
        self.net = nn.Sequential(*layers)
        self.output_dim = current_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class LabelClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        super().__init__()
        layers = []
        current_dim = input_dim
        for h_dim in hidden_dims:
            layers.extend([
                nn.Linear(current_dim, h_dim),
                nn.ReLU(inplace=True)
            ])
            current_dim = h_dim
        layers.extend([
            nn.Linear(current_dim, 1),
            nn.Sigmoid()
        ])
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class DomainClassifier(nn.Module):
    def __init__(self, input_dim: int, hidden_dims: List[int]):
        super().__init__()
        # GRL will be applied before the first linear layer
        self.grl = GradientReversalLayer(lambda_=1.0)
        
        layers = []
        current_dim = input_dim
        for h_dim in hidden_dims:
            layers.extend([
                nn.Linear(current_dim, h_dim),
                nn.ReLU(inplace=True)
            ])
            current_dim = h_dim
        layers.extend([
            nn.Linear(current_dim, 1),
            nn.Sigmoid()
        ])
        self.net = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor, lambda_: float = 1.0) -> torch.Tensor:
        self.grl.lambda_ = lambda_
        x = self.grl(x)
        return self.net(x)


class DANN(nn.Module):
    def __init__(self, input_dim: int,
                 feature_hidden_dims: List[int] = [128, 64],
                 label_hidden_dims: List[int] = [32],
                 domain_hidden_dims: List[int] = [32]):
        super().__init__()
        self.feature_extractor = FeatureExtractor(input_dim, feature_hidden_dims)
        self.label_classifier = LabelClassifier(self.feature_extractor.output_dim, label_hidden_dims)
        self.domain_classifier = DomainClassifier(self.feature_extractor.output_dim, domain_hidden_dims)

    def forward(self, x: torch.Tensor, lambda_: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        features = self.feature_extractor(x)
        label_output = self.label_classifier(features)
        domain_output = self.domain_classifier(features, lambda_)
        return label_output, domain_output, features

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        return self.feature_extractor(x)


def to_tensor(data: Union[np.ndarray, pd.DataFrame, pd.Series, torch.Tensor]) -> torch.Tensor:
    if isinstance(data, (pd.DataFrame, pd.Series)):
        return torch.tensor(data.values, dtype=torch.float32)
    elif isinstance(data, np.ndarray):
        return torch.tensor(data, dtype=torch.float32)
    elif isinstance(data, torch.Tensor):
        return data.float()
    return torch.tensor(data, dtype=torch.float32)


class DANNTrainer:
    def __init__(self, input_dim: int, config: Dict[str, Any]):
        self.config = config
        self.input_dim = input_dim
        
        # Parse nested config structure from domain_adaptation.yaml
        fe_config = config.get('feature_extractor', {})
        lc_config = config.get('label_classifier', {})
        dc_config = config.get('domain_classifier', {})
        train_config = config.get('training', {})
        
        self.feature_hidden_dims = fe_config.get('hidden_dims', [128, 64])
        self.label_hidden_dims = lc_config.get('hidden_dims', [32])
        self.domain_hidden_dims = dc_config.get('hidden_dims', [32])
        self.lr = train_config.get('lr', 1e-3)
        self.batch_size = train_config.get('batch_size', 64)
        self.epochs = train_config.get('epochs', 100)
        self.patience = train_config.get('patience', 10)
        self.seed = train_config.get('random_seed', 42)
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if self.seed is not None:
            torch.manual_seed(self.seed)
            np.random.seed(self.seed)

        self.model = DANN(
            input_dim=self.input_dim,
            feature_hidden_dims=self.feature_hidden_dims,
            label_hidden_dims=self.label_hidden_dims,
            domain_hidden_dims=self.domain_hidden_dims
        ).to(self.device)
        
        self.criterion_label = nn.BCELoss()
        self.criterion_domain = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

    def train(self, source_X, source_y, target_X, source_val_X, source_val_y, target_val_X=None) -> Dict[str, List[float]]:
        source_X = to_tensor(source_X)
        source_y = to_tensor(source_y).view(-1, 1)
        target_X = to_tensor(target_X)
        
        source_val_X = to_tensor(source_val_X)
        source_val_y = to_tensor(source_val_y).view(-1, 1)
        if target_val_X is not None:
            target_val_X = to_tensor(target_val_X)
        
        source_dataset = TensorDataset(source_X, source_y)
        target_dataset = TensorDataset(target_X, torch.zeros(target_X.size(0), 1))  # domain 0
        
        source_loader = DataLoader(source_dataset, batch_size=self.batch_size, shuffle=True, drop_last=True)
        target_loader = DataLoader(target_dataset, batch_size=self.batch_size, shuffle=True, drop_last=True)
        
        history = {
            'label_losses': [], 'domain_losses': [], 'total_losses': [],
            'val_losses': [], 'lambdas': [], 'domain_aucs': []
        }
        
        best_val_loss = float('inf')
        patience_counter = 0
        best_model_state = None
        
        total_steps = self.epochs * min(len(source_loader), len(target_loader))
        current_step = 0
        
        for epoch in range(self.epochs):
            self.model.train()
            
            epoch_label_loss = 0.0
            epoch_domain_loss = 0.0
            
            len_dataloader = min(len(source_loader), len(target_loader))
            source_iter = iter(source_loader)
            target_iter = iter(target_loader)
            
            all_domain_preds = []
            all_domain_labels = []

            for _ in range(len_dataloader):
                p = current_step / total_steps if total_steps > 0 else 1.0
                lambda_ = lambda_scheduler(p)
                
                s_X, s_y = next(source_iter)
                s_X, s_y = s_X.to(self.device), s_y.to(self.device)
                
                t_X, _ = next(target_iter)
                t_X = t_X.to(self.device)
                
                # Domain 1 for source, 0 for target
                domain_y_s = torch.ones(s_X.size(0), 1).to(self.device)
                domain_y_t = torch.zeros(t_X.size(0), 1).to(self.device)
                
                self.optimizer.zero_grad()
                
                label_out_s, domain_out_s, _ = self.model(s_X, lambda_)
                loss_label = self.criterion_label(label_out_s, s_y)
                loss_domain_s = self.criterion_domain(domain_out_s, domain_y_s)
                
                _, domain_out_t, _ = self.model(t_X, lambda_)
                loss_domain_t = self.criterion_domain(domain_out_t, domain_y_t)
                
                loss_domain = loss_domain_s + loss_domain_t
                loss = loss_label + loss_domain
                
                loss.backward()
                self.optimizer.step()
                
                epoch_label_loss += loss_label.item()
                epoch_domain_loss += loss_domain.item()
                
                all_domain_preds.extend(domain_out_s.detach().cpu().numpy())
                all_domain_preds.extend(domain_out_t.detach().cpu().numpy())
                all_domain_labels.extend(domain_y_s.cpu().numpy())
                all_domain_labels.extend(domain_y_t.cpu().numpy())
                
                current_step += 1

            self.model.eval()
            with torch.no_grad():
                val_X_dev = source_val_X.to(self.device)
                val_y_dev = source_val_y.to(self.device)
                val_preds, _, _ = self.model(val_X_dev, lambda_=0.0)
                val_loss = self.criterion_label(val_preds, val_y_dev).item()
            
            epoch_label_loss /= len_dataloader
            epoch_domain_loss /= len_dataloader
            total_loss = epoch_label_loss + epoch_domain_loss
            
            try:
                domain_auc = roc_auc_score(all_domain_labels, all_domain_preds)
            except ValueError:
                domain_auc = 0.5
                
            history['label_losses'].append(epoch_label_loss)
            history['domain_losses'].append(epoch_domain_loss)
            history['total_losses'].append(total_loss)
            history['val_losses'].append(val_loss)
            history['lambdas'].append(lambda_)
            history['domain_aucs'].append(domain_auc)
            
            print(f"Epoch {epoch+1}/{self.epochs} - Label Loss: {epoch_label_loss:.4f} - Domain Loss: {epoch_domain_loss:.4f} - Val Loss: {val_loss:.4f} - Lambda: {lambda_:.4f}")
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_model_state = copy.deepcopy(self.model.state_dict())
            else:
                patience_counter += 1
                
            if patience_counter >= self.patience:
                print(f"Early stopping at epoch {epoch+1}")
                break
                
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)
            
        return history

    def predict_proba(self, X) -> np.ndarray:
        self.model.eval()
        X_tensor = to_tensor(X).to(self.device)
        with torch.no_grad():
            preds, _, _ = self.model(X_tensor, lambda_=0.0)
        return preds.cpu().numpy().flatten()

    def predict(self, X, threshold: float = 0.5) -> np.ndarray:
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)
        
    def extract_features(self, X: Union[np.ndarray, pd.DataFrame, torch.Tensor]) -> np.ndarray:
        self.model.eval()
        X_tensor = to_tensor(X).to(self.device)
        with torch.no_grad():
            features = self.model.extract_features(X_tensor)
        return features.cpu().numpy()
        
    def save(self, path: str):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'config': self.config
        }, path)
        
    def load(self, path: str):
        checkpoint = torch.load(path, map_location=self.device)
        self.config = checkpoint.get('config', self.config)
        self.model.load_state_dict(checkpoint['model_state_dict'])
