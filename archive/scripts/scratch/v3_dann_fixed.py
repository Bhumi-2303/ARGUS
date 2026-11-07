import pandas as pd
import numpy as np
import os
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, confusion_matrix

class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)
    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.alpha, None

class DummyModule(nn.Module):
    pass

class DANNNetwork(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.1):
        super().__init__()
        self.feature_extractor = DummyModule()
        self.feature_extractor.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, latent_dim),
            nn.BatchNorm1d(latent_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(latent_dim, 16)
        )
        
        self.attack_classifier = DummyModule()
        self.attack_classifier.network = nn.Sequential(
            nn.Linear(16, 16),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(16, 1)
        )
        
        self.domain_classifier = DummyModule()
        self.domain_classifier.network = nn.Sequential(
            nn.Linear(16, 16),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(16, 1)
        )

    def forward(self, x: torch.Tensor, alpha: float = 1.0):
        features = self.feature_extractor.network(x)
        attack_logits = self.attack_classifier.network(features).squeeze(-1)
        reversed_features = GradReverse.apply(features, alpha)
        domain_logits = self.domain_classifier.network(reversed_features).squeeze(-1)
        return attack_logits, domain_logits, features

data_dir = "data/raw/legacy_package/argus_coral_data"
out_dir = "results/verification/predictions"
os.makedirs(out_dir, exist_ok=True)

print("\n--- Running DANN ---")
df_s = pd.read_csv(os.path.join(data_dir, "ciciot_train_features.csv"))
X_s = df_s.drop(columns=["label"]).values
scaler = StandardScaler().fit(X_s)

df_test = pd.read_csv(os.path.join(data_dir, "nfton_test_features.csv"))
X_test = df_test.drop(columns=["label"]).values
y_test = df_test['label'].values

X_test_scaled = scaler.transform(X_test).astype(np.float32)

model = DANNNetwork(input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.10)
ckpt = os.path.join(data_dir, "dann_results", "dann_best_model.pt")
model.load_state_dict(torch.load(ckpt, map_location='cpu', weights_only=False)['model_state_dict'])
model.eval()

with torch.no_grad():
    logits, _, _ = model(torch.tensor(X_test_scaled), alpha=0.0)
    proba_dann = torch.sigmoid(logits).cpu().numpy().astype(np.float32)

np.savez_compressed(os.path.join(out_dir, "DANN_preds.npz"), proba=proba_dann)

pred_dann = (proba_dann >= 0.60).astype(int)
roc_dann = roc_auc_score(y_test, proba_dann)
tn, fp, fn, tp = confusion_matrix(y_test, pred_dann).ravel()
spec_dann = tn / (tn + fp)
print(f"DANN -> ROC: {roc_dann:.4f}, Spec: {spec_dann:.4f}")
