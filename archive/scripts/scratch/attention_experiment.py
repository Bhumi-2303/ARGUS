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
import os
import json
import time
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# 1. SETUP DIRECTORIES
base_dir = "data/reproduction/attention"
dirs = ["attention", "transformer", "mlp", "dann", "plots", "metrics", "predictions", "reports", "manifests"]
for d in dirs:
    os.makedirs(os.path.join(base_dir, d), exist_ok=True)

# 2. LOAD AND MAP V2 FEATURES (EXACTLY AS BEFORE)
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

# 3. DEFINE MODELS
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
    def __init__(self, input_dim, is_transformer=False, ablations=None):
        super().__init__()
        self.is_transformer = is_transformer
        self.ablations = ablations or []
        
        # d=11: 0:dur, 1:pkts, 2:bytes, 3:bpp, 4:prate, 5:brate, 6+:proto
        self.gA_dim = 2 # pkts, bytes (1, 2)
        self.gB_dim = 3 # dur, prate, brate (0, 4, 5)
        self.gC_dim = 1 # bpp (3)
        self.gD_dim = input_dim - 6 # protocol
        
        embed_dim = 16
        self.embed_dim = embed_dim
        
        self.projA = nn.Linear(self.gA_dim, embed_dim)
        self.projB = nn.Linear(self.gB_dim, embed_dim)
        self.projC = nn.Linear(self.gC_dim, embed_dim)
        self.projD = nn.Linear(self.gD_dim, embed_dim)
        
        self.num_tokens = 4 - len(self.ablations)
        if self.num_tokens > 0:
            self.pos_emb = nn.Parameter(torch.randn(1, self.num_tokens, embed_dim))
        
        if is_transformer:
            encoder_layer = nn.TransformerEncoderLayer(d_model=embed_dim, nhead=4, dim_feedforward=32, batch_first=True, dropout=0.1)
            self.attention = nn.TransformerEncoder(encoder_layer, num_layers=2)
        else:
            self.attention = nn.MultiheadAttention(embed_dim, num_heads=4, batch_first=True, dropout=0.1)
        
        self.fusion = nn.Linear(self.num_tokens * embed_dim, 16)
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
        
        tokens = []
        if 'A' not in self.ablations: tokens.append(self.projA(A))
        if 'B' not in self.ablations: tokens.append(self.projB(B))
        if 'C' not in self.ablations: tokens.append(self.projC(C))
        if 'D' not in self.ablations: tokens.append(self.projD(D))
            
        if not tokens: # Extreme ablation fallback
            feat = torch.zeros(x.size(0), 16, device=x.device)
            class_out = self.classifier(feat)
            return class_out, None, feat, None

        x_tok = torch.stack(tokens, dim=1) # (batch, seq, embed_dim)
        x_tok = x_tok + self.pos_emb
        
        attn_weights = None
        if self.is_transformer:
            # TransformerEncoder doesn't return weights cleanly without hooks, we'll return None for simplicity
            x_att = self.attention(x_tok)
        else:
            x_att, attn_weights = self.attention(x_tok, x_tok, x_tok)
        
        feat = torch.relu(self.fusion(x_att.reshape(x_tok.size(0), -1)))
        
        class_out = self.classifier(feat)
        if alpha > 0:
            domain_out = self.domain(GradReverse.apply(feat, alpha))
            return class_out, domain_out, feat, attn_weights
        return class_out, None, feat, attn_weights

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

def get_metrics(y_true, y_prob, t=0.5):
    y_pred = (y_prob >= t).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    try: roc_auc = roc_auc_score(y_true, y_prob)
    except: roc_auc = np.nan
    try: pr_auc = average_precision_score(y_true, y_prob)
    except: pr_auc = np.nan
    tn, fp, fn, tp = cm.ravel()
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0
    return {
        "roc_auc": float(roc_auc), "pr_auc": float(pr_auc),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": float(spec),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "ppr": float((y_pred == 1).mean())
    }

SEEDS = [42, 43, 44, 45, 46]
EXPERIMENTS = {
    "MLP": {"is_dann": False, "type": "mlp"},
    "MLP-DANN": {"is_dann": True, "type": "mlp"},
    "Attention": {"is_dann": False, "type": "attn", "is_transformer": False},
    "Attention-DANN": {"is_dann": True, "type": "attn", "is_transformer": False},
    "Transformer": {"is_dann": False, "type": "attn", "is_transformer": True},
    "Transformer-DANN": {"is_dann": True, "type": "attn", "is_transformer": True},
}
# Ablations (run on Attention, No DANN)
ABLATIONS = {
    "No-Attention": {"is_dann": False, "type": "mlp"}, # E1 handles this, we'll just refer to MLP
    "Ablate-Protocol": {"is_dann": False, "type": "attn", "is_transformer": False, "abs": ['D']},
    "Ablate-Rate": {"is_dann": False, "type": "attn", "is_transformer": False, "abs": ['B']},
    "Ablate-Volume": {"is_dann": False, "type": "attn", "is_transformer": False, "abs": ['A']},
}
ALL_EXPS = {**EXPERIMENTS, **ABLATIONS}

results = {k: [] for k in ALL_EXPS.keys()}

print("Starting training loops...")
for seed in SEEDS:
    print(f"--- Seed {seed} ---")
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
    
    # Batch size 512, 10 epochs for faster turnaround while ensuring convergence
    loader = DataLoader(TensorDataset(src_tensor, src_labels), batch_size=4096, shuffle=True)
    val_tensor = torch.FloatTensor(X_val)
    
    for exp_name, conf in ALL_EXPS.items():
        print(f"  Running {exp_name}...")
        if conf['type'] == 'mlp':
            model = MLPBase(d)
        else:
            model = AttentionBase(d, is_transformer=conf.get('is_transformer', False), ablations=conf.get('abs', []))
            
        opt = optim.Adam(model.parameters(), lr=0.001)
        bce = nn.BCEWithLogitsLoss()
        
        start_time = time.time()
        for epoch in range(3):
            model.train()
            for bx, by in loader:
                alpha = 1.0 if conf['is_dann'] else 0.0
                out = model(bx, alpha)
                class_out = out[0]
                l_class = bce(class_out, by)
                loss = l_class
                
                if conf['is_dann']:
                    d_src = out[1]
                    l_ds = bce(d_src, torch.ones_like(d_src))
                    
                    idx = torch.randperm(len(tgt_tensor))[:len(bx)]
                    bt = tgt_tensor[idx]
                    out_tgt = model(bt, alpha)
                    d_tgt = out_tgt[1]
                    l_dt = bce(d_tgt, torch.zeros_like(d_tgt))
                    
                    loss = l_class + 0.5 * (l_ds + l_dt)
                    
                opt.zero_grad()
                loss.backward()
                opt.step()
                
        train_time = time.time() - start_time
        
        # Eval
        model.eval()
        with torch.no_grad():
            out_val = model(val_tensor)
            val_prob = torch.sigmoid(out_val[0]).numpy().flatten()
            
            # Thresholding
            best_thresh, best_f1 = 0.5, 0.0
            from sklearn.metrics import f1_score as f1s
            for t in np.linspace(0.1, 0.9, 17):
                f1 = f1s(y_val, (val_prob >= t).astype(int), zero_division=0)
                if f1 > best_f1: best_f1, best_thresh = f1, t
            
            out_test = model(tgt_tensor)
            test_prob = torch.sigmoid(out_test[0]).numpy().flatten()
            
        metrics = get_metrics(y_test, test_prob, best_thresh)
        metrics['threshold'] = float(best_thresh)
        metrics['train_time'] = train_time
        metrics['params'] = count_parameters(model)
        
        # Save attention weights for Seed 42, Attention models
        if seed == 42 and conf['type'] == 'attn' and not conf.get('is_transformer', False):
            attn_weights = out_test[3]
            if attn_weights is not None:
                aw_mean = attn_weights.mean(dim=0).numpy().tolist()
                with open(f"{base_dir}/metrics/attn_{exp_name}_seed42.json", "w") as f:
                    json.dump(aw_mean, f)
                    
        results[exp_name].append(metrics)

with open(f"{base_dir}/metrics/all_results.json", "w") as f:
    json.dump(results, f, indent=2)

def agg(res_list):
    keys = res_list[0].keys()
    out = {}
    for k in keys:
        vals = [r[k] for r in res_list]
        out[k] = {"mean": np.nanmean(vals), "std": np.nanstd(vals)}
    return out

agg_res = {k: agg(v) for k, v in results.items()}
with open(f"{base_dir}/metrics/aggregated.json", "w") as f:
    json.dump(agg_res, f, indent=2)

print("Experiment completed.")
