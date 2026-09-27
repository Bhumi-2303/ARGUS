import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score, 
                             precision_score, recall_score, balanced_accuracy_score, 
                             confusion_matrix)
import matplotlib.pyplot as plt
import os
import json
import warnings
warnings.filterwarnings('ignore')

out_dir = "data/reproduction/attention/threshold_sensitivity/"
os.makedirs(out_dir, exist_ok=True)

print("Loading datasets...")
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
del ciciot_raw, nfton_raw, bot_raw, source_with_indicator

class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, alpha):
        ctx.alpha = float(alpha)
        return x.view_as(x)
    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.alpha, None

class MLPBase(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.feature = nn.Sequential(nn.Linear(input_dim, 32), nn.ReLU(), nn.Linear(32, 16), nn.ReLU())
        self.classifier = nn.Linear(16, 1)
        self.domain = nn.Sequential(nn.Linear(16, 16), nn.ReLU(), nn.Linear(16, 1))
    
    def forward(self, x, alpha=0.0):
        feat = self.feature(x)
        class_out = self.classifier(feat)
        if alpha > 0:
            domain_out = self.domain(GradReverse.apply(feat, alpha))
            return class_out, domain_out, feat
        return class_out, None, feat

class AttentionBase(nn.Module):
    def __init__(self, input_dim, is_transformer=False):
        super().__init__()
        self.is_transformer = is_transformer
        self.projA = nn.Linear(2, 16)
        self.projB = nn.Linear(3, 16)
        self.projC = nn.Linear(1, 16)
        self.projD = nn.Linear(input_dim - 6, 16)
        self.pos_emb = nn.Parameter(torch.randn(1, 4, 16))
        
        if is_transformer:
            encoder_layer = nn.TransformerEncoderLayer(d_model=16, nhead=4, dim_feedforward=32, batch_first=True, dropout=0.1)
            self.attention = nn.TransformerEncoder(encoder_layer, num_layers=2)
        else:
            self.attention = nn.MultiheadAttention(16, num_heads=4, batch_first=True, dropout=0.1)
        self.fusion = nn.Linear(64, 16)
        self.classifier = nn.Linear(16, 1)
        self.domain = nn.Sequential(nn.Linear(16, 16), nn.ReLU(), nn.Linear(16, 1))

    def extract_groups(self, x):
        A = x[:, [1, 2]]
        B = x[:, [0, 4, 5]]
        C = x[:, [3]]
        D = x[:, 6:]
        return A, B, C, D

    def forward(self, x, alpha=0.0):
        A, B, C, D = self.extract_groups(x)
        tokens = [self.projA(A), self.projB(B), self.projC(C), self.projD(D)]
        x_tok = torch.stack(tokens, dim=1) + self.pos_emb
        if self.is_transformer:
            x_att = self.attention(x_tok)
        else:
            x_att, _ = self.attention(x_tok, x_tok, x_tok)
        feat = torch.relu(self.fusion(x_att.reshape(x_tok.size(0), -1)))
        class_out = self.classifier(feat)
        if alpha > 0:
            domain_out = self.domain(GradReverse.apply(feat, alpha))
            return class_out, domain_out, feat
        return class_out, None, feat

SEEDS = [42, 43, 44, 45, 46]
MODELS = {
    "MLP": {"is_dann": False, "type": "mlp"},
    "MLP-DANN": {"is_dann": True, "type": "mlp"},
    "Attention": {"is_dann": False, "type": "attn", "is_transformer": False},
    "Attention-DANN": {"is_dann": True, "type": "attn", "is_transformer": False},
    "Transformer": {"is_dann": False, "type": "attn", "is_transformer": True},
    "Transformer-DANN": {"is_dann": True, "type": "attn", "is_transformer": True},
}

all_thresh_metrics = []
source_thresholds = []
dist_summaries = []

print("Starting training and threshold evaluation...")
for seed in SEEDS:
    print(f"Seed {seed}...")
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
    
    src_tensor = torch.FloatTensor(X_train)
    src_labels = torch.FloatTensor(y_train).unsqueeze(1)
    tgt_tensor = torch.FloatTensor(X_test)
    val_tensor = torch.FloatTensor(X_val)
    
    loader = DataLoader(TensorDataset(src_tensor, src_labels), batch_size=4096, shuffle=True)
    
    for m_name, conf in MODELS.items():
        if conf['type'] == 'mlp':
            model = MLPBase(d)
        else:
            model = AttentionBase(d, is_transformer=conf.get('is_transformer', False))
            
        opt = optim.Adam(model.parameters(), lr=0.001)
        bce = nn.BCEWithLogitsLoss()
        
        for epoch in range(3):
            model.train()
            for bx, by in loader:
                alpha = 1.0 if conf['is_dann'] else 0.0
                out = model(bx, alpha)
                l_class = bce(out[0], by)
                loss = l_class
                if conf['is_dann']:
                    d_src = out[1]
                    l_ds = bce(d_src, torch.ones_like(d_src))
                    idx = torch.randperm(len(tgt_tensor))[:len(bx)]
                    bt = tgt_tensor[idx]
                    out_tgt = model(bt, alpha)
                    l_dt = bce(out_tgt[1], torch.zeros_like(out_tgt[1]))
                    loss = l_class + 0.5 * (l_ds + l_dt)
                opt.zero_grad()
                loss.backward()
                opt.step()
                
        model.eval()
        with torch.no_grad():
            out_val = model(val_tensor)
            val_prob = torch.sigmoid(out_val[0]).numpy().flatten()
            
            out_test = model(tgt_tensor)
            test_prob = torch.sigmoid(out_test[0]).numpy().flatten()
            
        # 1. Source Validation Threshold
        best_thresh, best_f1 = 0.5, 0.0
        from sklearn.metrics import f1_score as f1s
        # 0.1 to 0.9 was used originally
        for t in np.linspace(0.1, 0.9, 17):
            f1 = f1s(y_val, (val_prob >= t).astype(int), zero_division=0)
            if f1 > best_f1: best_f1, best_thresh = f1, t
            
        source_thresholds.append({
            "model": m_name, "seed": seed, 
            "source_f1": float(best_f1), "selected_threshold": float(best_thresh)
        })
        
        # 2. Prediction Distribution Summary
        dist_summaries.append({
            "model": m_name, "seed": seed,
            "target_mean_prob": float(test_prob.mean()),
            "target_std_prob": float(test_prob.std()),
            "target_min_prob": float(test_prob.min()),
            "target_max_prob": float(test_prob.max()),
            "target_p25": float(np.percentile(test_prob, 25)),
            "target_p50": float(np.percentile(test_prob, 50)),
            "target_p75": float(np.percentile(test_prob, 75))
        })
        
        # 3. Target Evaluation across 101 thresholds
        try: pr_auc = average_precision_score(y_test, test_prob)
        except: pr_auc = np.nan
        try: roc_auc = roc_auc_score(y_test, test_prob)
        except: roc_auc = np.nan
            
        thresholds = np.linspace(0.0, 1.0, 101)
        for t in thresholds:
            y_pred = (test_prob >= t).astype(int)
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            
            # Save
            all_thresh_metrics.append({
                "model": m_name, "seed": seed, "threshold": float(t),
                "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "specificity": float(spec),
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "f1": float(f1_score(y_test, y_pred, zero_division=0)),
                "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
                "ppr": float((y_pred == 1).mean()),
                "pr_auc": float(pr_auc), "roc_auc": float(roc_auc)
            })

df_metrics = pd.DataFrame(all_thresh_metrics)
df_metrics.to_csv(f"{out_dir}/threshold_metrics_per_seed.csv", index=False)

df_src_thresh = pd.DataFrame(source_thresholds)
df_src_thresh.to_csv(f"{out_dir}/source_thresholds.csv", index=False)

df_dist = pd.DataFrame(dist_summaries)
df_dist.to_csv(f"{out_dir}/prediction_distribution_summary.csv", index=False)

# Aggregate
grouped = df_metrics.groupby(['model', 'threshold']).agg('mean').reset_index().drop(columns=['seed'])
grouped.to_csv(f"{out_dir}/threshold_metrics_aggregated.csv", index=False)

# Plotting
print("Generating figures...")
metrics_to_plot = {
    'recall': 'Threshold vs Recall',
    'specificity': 'Threshold vs Specificity',
    'precision': 'Threshold vs Precision',
    'f1': 'Threshold vs F1',
    'balanced_accuracy': 'Threshold vs Balanced Accuracy',
    'ppr': 'Threshold vs Positive Prediction Rate'
}

for m_key, title in metrics_to_plot.items():
    plt.figure(figsize=(10, 6))
    for m_name in MODELS.keys():
        sub = grouped[grouped['model'] == m_name]
        plt.plot(sub['threshold'], sub[m_key], label=m_name)
    plt.title(title)
    plt.xlabel("Decision Threshold")
    plt.ylabel(m_key.replace('_', ' ').title())
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{out_dir}/threshold_{m_key}.png")
    plt.close()

# Config & Manifest
with open(f"{out_dir}/config.json", "w") as f:
    json.dump({"thresholds": 101, "range": "[0.0, 1.0]", "step": 0.01}, f)

with open(f"{out_dir}/manifest.json", "w") as f:
    json.dump({"run": "threshold_sensitivity", "status": "completed"}, f)

print("Finished!")
