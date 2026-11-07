import numpy as np
import pandas as pd
import xgboost as xgb
import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import roc_auc_score, average_precision_score, f1_score, precision_score, recall_score, balanced_accuracy_score, confusion_matrix
import scipy.linalg
from torch.utils.data import DataLoader, TensorDataset

# Set seeds
np.random.seed(42)
torch.manual_seed(42)

# Load Data
data = np.load('data/reproduction/preprocessing/preprocessed_data.npz')
X_train, y_train = data['X_train'], data['y_train']
X_val, y_val = data['X_val'], data['y_val']
X_test, y_test = data['X_test'], data['y_test']

def evaluate_model(y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    try:
        roc_auc = roc_auc_score(y_true, y_prob)
    except:
        roc_auc = 0.5
    try:
        pr_auc = average_precision_score(y_true, y_prob)
    except:
        pr_auc = 0.0
    return {
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "confusion_matrix": cm.tolist(),
        "fpr": float(cm[0,1] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0),
        "fnr": float(cm[1,0] / (cm[1,0] + cm[1,1]) if (cm[1,0] + cm[1,1]) > 0 else 0),
        "samples": len(y_true),
        "attack_samples": int(sum(y_true)),
        "benign_samples": int(len(y_true) - sum(y_true))
    }

def save_predictions(name, y_true, y_prob, threshold=0.5):
    y_pred = (y_prob >= threshold).astype(int)
    df = pd.DataFrame({
        "sample_identifier": range(len(y_true)),
        "true_label": y_true,
        "predicted_probability": y_prob,
        "predicted_class": y_pred,
        "domain": "BoT-IoT"
    })
    df.to_csv(f"data/reproduction/{name}/predictions.csv", index=False)

# ----------------- PHASE 5: Source-Only XGBoost -----------------
os.makedirs("data/reproduction/source_only", exist_ok=True)
clf_src = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, early_stopping_rounds=10)
clf_src.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False, )

prob_test_src = clf_src.predict_proba(X_test)[:, 1]
metrics_src = evaluate_model(y_test, prob_test_src, threshold=0.5)

with open("data/reproduction/source_only/metrics.json", "w") as f:
    json.dump(metrics_src, f, indent=2)
save_predictions("source_only", y_test, prob_test_src, 0.5)

# ----------------- PHASE 6: Classical CORAL -----------------
os.makedirs("data/reproduction/coral", exist_ok=True)
# Target unlabeled features are used to align SOURCE to TARGET
cov_src = np.cov(X_train, rowvar=False) + np.eye(X_train.shape[1]) * 1e-6
cov_tgt = np.cov(X_test, rowvar=False) + np.eye(X_test.shape[1]) * 1e-6

A_src = scipy.linalg.inv(scipy.linalg.sqrtm(cov_src))
A_tgt = scipy.linalg.sqrtm(cov_tgt)
coral_matrix = A_src.dot(A_tgt)

X_train_coral = X_train.dot(coral_matrix).real
X_val_coral = X_val.dot(coral_matrix).real
X_test_coral = X_test # Target is untouched, source is aligned to target

clf_coral = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, early_stopping_rounds=10)
clf_coral.fit(X_train_coral, y_train, eval_set=[(X_val_coral, y_val)], verbose=False, )

prob_test_coral = clf_coral.predict_proba(X_test_coral)[:, 1]
metrics_coral = evaluate_model(y_test, prob_test_coral, threshold=0.5)

with open("data/reproduction/coral/metrics.json", "w") as f:
    json.dump(metrics_coral, f, indent=2)
save_predictions("coral", y_test, prob_test_coral, 0.5)

# ----------------- PHASE 7: DANN (PyTorch) -----------------
os.makedirs("data/reproduction/dann", exist_ok=True)

class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = float(alpha)
        return x.view_as(x)
    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.alpha, None

class DANN(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.feature = nn.Sequential(nn.Linear(input_dim, 32), nn.ReLU(), nn.Linear(32, 16), nn.ReLU())
        self.classifier = nn.Sequential(nn.Linear(16, 1))
        self.domain = nn.Sequential(nn.Linear(16, 16), nn.ReLU(), nn.Linear(16, 1))
    
    def forward(self, x, alpha=1.0):
        feat = self.feature(x)
        class_out = self.classifier(feat)
        feat_rev = GradReverse.apply(feat, alpha)
        domain_out = self.domain(feat_rev)
        return class_out, domain_out

# We must use source labeled data, and target unlabeled data.
# For target unlabeled data, we cycle through the small BoT-IoT test set.
model = DANN(input_dim=X_train.shape[1])
optimizer = optim.Adam(model.parameters(), lr=0.001)
bce = nn.BCEWithLogitsLoss()

# Dataloaders
src_tensor = torch.FloatTensor(X_train)
src_labels = torch.FloatTensor(y_train).unsqueeze(1)
tgt_tensor = torch.FloatTensor(X_test)
tgt_labels = torch.zeros(len(X_test), 1) # domain label 0 for target, 1 for source

src_loader = DataLoader(TensorDataset(src_tensor, src_labels), batch_size=256, shuffle=True)

for epoch in range(15): # Fast training for 15 epochs
    model.train()
    for batch_x, batch_y in src_loader:
        # Source classification
        class_out, dom_out_src = model(batch_x, alpha=1.0)
        loss_class = bce(class_out, batch_y)
        loss_dom_src = bce(dom_out_src, torch.ones_like(dom_out_src)) # 1 for source
        
        # Target domain
        idx = torch.randperm(len(tgt_tensor))[:len(batch_x)]
        batch_tgt = tgt_tensor[idx]
        _, dom_out_tgt = model(batch_tgt, alpha=1.0)
        loss_dom_tgt = bce(dom_out_tgt, torch.zeros_like(dom_out_tgt)) # 0 for target
        
        loss = loss_class + 0.5 * (loss_dom_src + loss_dom_tgt)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

model.eval()
with torch.no_grad():
    val_out, _ = model(torch.FloatTensor(X_val))
    val_prob = torch.sigmoid(val_out).numpy().flatten()
    # Select threshold using SOURCE VALIDATION (F1-score)
    thresholds = np.linspace(0.1, 0.9, 9)
    best_thresh, best_f1 = 0.5, 0.0
    for t in thresholds:
        f1 = f1_score(y_val, (val_prob >= t).astype(int), zero_division=0)
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = t
    
    test_out, _ = model(torch.FloatTensor(X_test))
    prob_test_dann = torch.sigmoid(test_out).numpy().flatten()
    # Write a unit test output confirming the probability index is positive
    # Yes, we have 1 output node with sigmoid. Close to 1 means label 1 (Attack).
    # Since we train loss_class = bce(class_out, batch_y), where attack is 1, this is guaranteed.

metrics_dann = evaluate_model(y_test, prob_test_dann, threshold=best_thresh)

with open("data/reproduction/dann/metrics.json", "w") as f:
    json.dump(metrics_dann, f, indent=2)
save_predictions("dann", y_test, prob_test_dann, best_thresh)

print("Training phases complete.")
print(f"DANN chosen threshold: {best_thresh}")
