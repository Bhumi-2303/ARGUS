import pandas as pd
import numpy as np
import os
import time
from xgboost import XGBClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn

class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = alpha
        return x.view_as(x)
    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.alpha, None

class DANNNetwork(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.1):
        super().__init__()
        self.feature_encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, latent_dim),
            nn.BatchNorm1d(latent_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout)
        )
        self.attack_classifier = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 1)
        )
        self.domain_classifier = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(inplace=True),
            nn.Linear(16, 1)
        )

    def forward(self, x: torch.Tensor, alpha: float = 1.0):
        features = self.feature_encoder(x)
        attack_logits = self.attack_classifier(features).squeeze(-1)
        reversed_features = GradReverse.apply(features, alpha)
        domain_logits = self.domain_classifier(reversed_features).squeeze(-1)
        return attack_logits, domain_logits, features

data_dir = "data/raw/legacy_package/argus_coral_data"
out_dir = "results/verification/predictions"
os.makedirs(out_dir, exist_ok=True)

def train_eval_xgb(train_file, test_file, exp_name, th=0.5):
    print(f"\n--- Running {exp_name} ---")
    t0 = time.time()
    
    df_train = pd.read_csv(os.path.join(data_dir, train_file))
    X_train = df_train.drop(columns=['label']).values
    y_train = df_train['label'].values
    
    xgb = XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42, n_jobs=-1, use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X_train, y_train)
    
    df_test = pd.read_csv(os.path.join(data_dir, test_file))
    X_test = df_test.drop(columns=['label']).values
    y_test = df_test['label'].values
    
    proba = xgb.predict_proba(X_test)[:, 1].astype(np.float32)
    np.savez_compressed(os.path.join(out_dir, f"{exp_name}_preds.npz"), proba=proba)
    
    pred = (proba >= th).astype(int)
    roc = roc_auc_score(y_test, proba)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    spec = tn / (tn + fp)
    t1 = time.time()
    print(f"{exp_name} completed in {t1-t0:.1f}s. ROC: {roc:.4f}, Spec: {spec:.4f}")
    return roc, spec

# Experiment A
roc_A, spec_A = train_eval_xgb("ciciot_train_features.csv", "ciciot_test_features.csv", "A_source_only_CICIoT")
# Experiment B
roc_B, spec_B = train_eval_xgb("ciciot_train_features.csv", "nfton_test_features.csv", "B_source_only_NFToN")
# Experiment C
roc_C, spec_C = train_eval_xgb("nfton_train_features.csv", "nfton_test_features.csv", "C_target_only_NFToN")
# Experiment D
roc_D, spec_D = train_eval_xgb("nfton_train_features.csv", "ciciot_test_features.csv", "D_target_only_CICIoT")

# Global CORAL
roc_g_coral, spec_g_coral = train_eval_xgb("ciciot_train_coral_aligned.csv", "nfton_test_features.csv", "Global_CORAL")

# Diagnostic Class-aware CORAL
roc_d_coral, spec_d_coral = train_eval_xgb("ciciot_train_class_aware_coral.csv", "nfton_test_features.csv", "Diagnostic_Class_Aware_CORAL")


print("\n--- Running Clean Class-Aware CORAL ---")
df_train = pd.read_csv(os.path.join(data_dir, "ciciot_train_clean_class_aware_coral.csv"))
X_train = df_train.drop(columns=['label']).values
y_train = df_train['label'].values
xgb_clean = XGBClassifier(n_estimators=200, max_depth=8, learning_rate=0.1, random_state=42, n_jobs=-1, use_label_encoder=False, eval_metric='logloss')
xgb_clean.fit(X_train, y_train)

# Threshold tuning
df_calib = pd.read_csv(os.path.join(data_dir, "nfton_train_calibration.csv"))
X_calib = df_calib.drop(columns=['label']).values
y_calib = df_calib['label'].values
calib_proba = xgb_clean.predict_proba(X_calib)[:, 1]

best_th = 0.50
best_f1_cal = -1.0
for th in np.linspace(0.01, 0.99, 99):
    p_val = (calib_proba >= th).astype(int)
    tp = np.sum((y_calib == 1) & (p_val == 1))
    fp = np.sum((y_calib == 0) & (p_val == 1))
    fn = np.sum((y_calib == 1) & (p_val == 0))
    f1_c = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
    if f1_c > best_f1_cal:
        best_f1_cal = f1_c
        best_th = float(th)

print(f"Calibrated Threshold for Clean CORAL: {best_th:.2f}")
df_test = pd.read_csv(os.path.join(data_dir, "nfton_test_features.csv"))
X_test = df_test.drop(columns=['label']).values
y_test = df_test['label'].values
proba = xgb_clean.predict_proba(X_test)[:, 1].astype(np.float32)
np.savez_compressed(os.path.join(out_dir, "Clean_Class_Aware_CORAL_preds.npz"), proba=proba)

pred = (proba >= best_th).astype(int)
roc_c_coral = roc_auc_score(y_test, proba)
tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
spec_c_coral = tn / (tn + fp)
print(f"Clean Class-Aware CORAL -> ROC: {roc_c_coral:.4f}, Spec: {spec_c_coral:.4f}")

print("\n--- Running DANN ---")
df_s = pd.read_csv(os.path.join(data_dir, "ciciot_train_features.csv"))
X_s = df_s.drop(columns=["label"]).values
scaler = StandardScaler().fit(X_s)

X_test_scaled = scaler.transform(X_test).astype(np.float32)
y_test_dann = y_test # from nfton_test

model = DANNNetwork(input_dim=4, hidden_dim=64, latent_dim=32, dropout=0.10)
ckpt = os.path.join(data_dir, "dann_results", "dann_best_model.pt")
model.load_state_dict(torch.load(ckpt, map_location='cpu'))
model.eval()

with torch.no_grad():
    logits, _, _ = model(torch.tensor(X_test_scaled), alpha=0.0)
    proba_dann = torch.sigmoid(logits).cpu().numpy().astype(np.float32)

np.savez_compressed(os.path.join(out_dir, "DANN_preds.npz"), proba=proba_dann)

pred_dann = (proba_dann >= 0.60).astype(int)
roc_dann = roc_auc_score(y_test_dann, proba_dann)
tn, fp, fn, tp = confusion_matrix(y_test_dann, pred_dann).ravel()
spec_dann = tn / (tn + fp)
print(f"DANN -> ROC: {roc_dann:.4f}, Spec: {spec_dann:.4f}")

