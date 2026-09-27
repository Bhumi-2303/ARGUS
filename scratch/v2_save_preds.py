import pandas as pd
import numpy as np
import xgboost as xgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import scipy.linalg
import os
import warnings
warnings.filterwarnings('ignore')

ciciot_raw = pd.read_csv("data/raw/cic_iot_2023/processed/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv")
nfton_raw = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet")
bot_raw = pd.read_csv("data/raw/bot_iot/raw/BoT-IoT dataset/csv/data_32.csv", low_memory=False)

protocol_map = {6: 'TCP', 17: 'UDP', 1: 'ICMP', 2054: 'ARP', 58: 'IPv6-ICMP'}
def map_bot_proto(p):
    p = str(p).lower()
    if p == 'tcp': return 'TCP'
    if p == 'udp': return 'UDP'
    if p == 'icmp': return 'ICMP'
    if p == 'arp': return 'ARP'
    if p == 'ipv6-icmp': return 'IPv6-ICMP'
    return 'Other'

df_cic = pd.DataFrame()
df_cic['duration'] = ciciot_raw['flow_duration']
df_cic['total_pkts'] = ciciot_raw['Number']
df_cic['total_bytes'] = ciciot_raw['Tot sum']
df_cic['protocol'] = ciciot_raw['Protocol Type'].map(protocol_map).fillna('Other')
df_cic['label'] = (ciciot_raw['label'] != 'BenignTraffic').astype(int)

df_nft = pd.DataFrame()
df_nft['duration'] = nfton_raw['FLOW_DURATION_MILLISECONDS'] / 1000.0
df_nft['total_pkts'] = nfton_raw['IN_PKTS'] + nfton_raw['OUT_PKTS']
df_nft['total_bytes'] = nfton_raw['IN_BYTES'] + nfton_raw['OUT_BYTES']
df_nft['protocol'] = nfton_raw['PROTOCOL'].map(protocol_map).fillna('Other')
df_nft['label'] = (nfton_raw['Label'] == 1).astype(int)

df_bot = pd.DataFrame()
df_bot['duration'] = bot_raw['dur']
df_bot['total_pkts'] = bot_raw['pkts']
df_bot['total_bytes'] = bot_raw['bytes']
df_bot['protocol'] = bot_raw['proto'].apply(map_bot_proto)
df_bot['label'] = (bot_raw['attack'] == 1).astype(int)

for df in [df_cic, df_nft, df_bot]:
    df['bytes_per_packet'] = df['total_bytes'] / np.maximum(df['total_pkts'], 1)
    df['packet_rate'] = df['total_pkts'] / np.maximum(df['duration'], 0.001)
    df['byte_rate'] = df['total_bytes'] / np.maximum(df['duration'], 0.001)

v2_cols = ['duration', 'total_pkts', 'total_bytes', 'protocol', 'bytes_per_packet', 'packet_rate', 'byte_rate']

df_cic = df_cic.drop_duplicates(subset=v2_cols)
df_nft = df_nft.drop_duplicates(subset=v2_cols)
df_bot = df_bot.drop_duplicates(subset=v2_cols)

df_source = pd.concat([df_cic, df_nft], ignore_index=True)
df_source = df_source.drop_duplicates(subset=v2_cols)

source_with_indicator = df_source.merge(df_bot[v2_cols], on=v2_cols, how='left', indicator=True)
df_source_clean = source_with_indicator[source_with_indicator['_merge'] == 'left_only'].drop(columns=['_merge'])

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

def save_preds(seed, model_name, y_true, y_prob, threshold):
    y_pred = (y_prob >= threshold).astype(int)
    df = pd.DataFrame({
        "sample_id": np.arange(len(y_true)),
        "true_label": y_true,
        "predicted_probability": y_prob,
        "predicted_label": y_pred,
        "model": model_name,
        "seed": seed
    })
    df.to_csv(f"data/reproduction/v2/predictions/preds_{model_name}_seed{seed}.csv", index=False)

SEEDS = [42, 43, 44, 45, 46]
for seed in SEEDS:
    print(f"Running seed {seed}")
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    df_train, df_val = train_test_split(df_source_clean, test_size=0.2, random_state=seed, stratify=df_source_clean['label'])
    
    ct = ColumnTransformer([
        ("num", StandardScaler(), ['duration', 'total_pkts', 'total_bytes', 'bytes_per_packet', 'packet_rate', 'byte_rate']),
        ("cat", OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['protocol'])
    ], remainder='drop')
    
    X_train = ct.fit_transform(df_train)
    X_val = ct.transform(df_val)
    X_test = ct.transform(df_bot)
    
    y_train = df_train['label'].values
    y_val = df_val['label'].values
    y_test = df_bot['label'].values
    d = X_train.shape[1]
    
    clf_src = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=seed, early_stopping_rounds=10)
    clf_src.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    
    val_prob_src = clf_src.predict_proba(X_val)[:, 1]
    from sklearn.metrics import f1_score
    best_thresh_src, best_f1 = 0.5, 0.0
    for t in np.linspace(0.1, 0.9, 9):
        f1 = f1_score(y_val, (val_prob_src >= t).astype(int), zero_division=0)
        if f1 > best_f1: best_f1, best_thresh_src = f1, t
            
    test_prob_src = clf_src.predict_proba(X_test)[:, 1]
    save_preds(seed, "source_only", y_test, test_prob_src, best_thresh_src)
    
    cov_src = np.cov(X_train, rowvar=False) + np.eye(d) * 1e-6
    cov_tgt = np.cov(X_test, rowvar=False) + np.eye(d) * 1e-6
    A_src = scipy.linalg.inv(scipy.linalg.sqrtm(cov_src))
    A_tgt = scipy.linalg.sqrtm(cov_tgt)
    coral_matrix = A_src.dot(A_tgt)
    
    X_train_coral = X_train.dot(coral_matrix).real
    X_val_coral = X_val.dot(coral_matrix).real
    
    clf_coral = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=seed, early_stopping_rounds=10)
    clf_coral.fit(X_train_coral, y_train, eval_set=[(X_val_coral, y_val)], verbose=False)
    
    val_prob_cor = clf_coral.predict_proba(X_val_coral)[:, 1]
    best_thresh_cor, best_f1 = 0.5, 0.0
    for t in np.linspace(0.1, 0.9, 9):
        f1 = f1_score(y_val, (val_prob_cor >= t).astype(int), zero_division=0)
        if f1 > best_f1: best_f1, best_thresh_cor = f1, t
            
    test_prob_cor = clf_coral.predict_proba(X_test)[:, 1]
    save_preds(seed, "coral", y_test, test_prob_cor, best_thresh_cor)
    
    model = DANN(input_dim=d)
    opt = optim.Adam(model.parameters(), lr=0.001)
    bce = nn.BCEWithLogitsLoss()
    src_tensor = torch.FloatTensor(X_train)
    src_labels = torch.FloatTensor(y_train).unsqueeze(1)
    tgt_tensor = torch.FloatTensor(X_test)
    loader = DataLoader(TensorDataset(src_tensor, src_labels), batch_size=256, shuffle=True)
    
    for epoch in range(15):
        model.train()
        for bx, by in loader:
            co, d_src = model(bx, alpha=1.0)
            l_class = bce(co, by)
            l_ds = bce(d_src, torch.ones_like(d_src))
            idx = torch.randperm(len(tgt_tensor))[:len(bx)]
            bt = tgt_tensor[idx]
            _, d_tgt = model(bt, alpha=1.0)
            l_dt = bce(d_tgt, torch.zeros_like(d_tgt))
            loss = l_class + 0.5 * (l_ds + l_dt)
            opt.zero_grad()
            loss.backward()
            opt.step()
            
    model.eval()
    with torch.no_grad():
        val_prob_dan = torch.sigmoid(model(torch.FloatTensor(X_val))[0]).numpy().flatten()
        best_thresh_dan, best_f1 = 0.5, 0.0
        for t in np.linspace(0.1, 0.9, 9):
            f1 = f1_score(y_val, (val_prob_dan >= t).astype(int), zero_division=0)
            if f1 > best_f1: best_f1, best_thresh_dan = f1, t
                
        test_prob_dan = torch.sigmoid(model(torch.FloatTensor(X_test))[0]).numpy().flatten()
    save_preds(seed, "dann", y_test, test_prob_dan, best_thresh_dan)

print("All predictions saved successfully")
