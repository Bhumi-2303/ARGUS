import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances
import matplotlib.pyplot as plt
import os
import json
import warnings
warnings.filterwarnings('ignore')

out_dir = "data/reproduction/attention/latent_analysis/"
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

domain_sep_metrics = []
class_sep_metrics = []
score_dist_metrics = []
latent_stats = []

print("Starting latent analysis...")
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
        
        # Train
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
                
        # Inference
        model.eval()
        with torch.no_grad():
            out_val = model(val_tensor)
            prob_val = torch.sigmoid(out_val[0]).numpy().flatten()
            feat_val = out_val[2].numpy()
            
            out_test = model(tgt_tensor)
            prob_test = torch.sigmoid(out_test[0]).numpy().flatten()
            feat_tgt = out_test[2].numpy()

        # Split domains and classes
        src_benign_idx = (y_val == 0)
        src_attack_idx = (y_val == 1)
        tgt_benign_idx = (y_test == 0)
        tgt_attack_idx = (y_test == 1)
        
        feat_src_benign = feat_val[src_benign_idx]
        feat_src_attack = feat_val[src_attack_idx]
        feat_tgt_benign = feat_tgt[tgt_benign_idx]
        feat_tgt_attack = feat_tgt[tgt_attack_idx]
        
        # Class centroids
        c_src_benign = feat_src_benign.mean(axis=0) if len(feat_src_benign)>0 else np.zeros(16)
        c_src_attack = feat_src_attack.mean(axis=0) if len(feat_src_attack)>0 else np.zeros(16)
        c_tgt_benign = feat_tgt_benign.mean(axis=0) if len(feat_tgt_benign)>0 else np.zeros(16)
        c_tgt_attack = feat_tgt_attack.mean(axis=0) if len(feat_tgt_attack)>0 else np.zeros(16)
        
        # Domain centroids
        c_src = feat_val.mean(axis=0)
        c_tgt = feat_tgt.mean(axis=0)
        
        dist_src_tgt = np.linalg.norm(c_src - c_tgt)
        dist_src_classes = np.linalg.norm(c_src_benign - c_src_attack)
        dist_tgt_classes = np.linalg.norm(c_tgt_benign - c_tgt_attack)
        
        # Domain separation accuracy
        # Subsample target to match source validation size for balance, or just use all
        X_domain = np.vstack([feat_val, feat_tgt])
        y_domain = np.concatenate([np.zeros(len(feat_val)), np.ones(len(feat_tgt))])
        
        # 3-fold CV logistic regression for fast domain discriminability measure
        clf = LogisticRegression(max_iter=100)
        # Random subset to keep it fast
        idx = np.random.choice(len(X_domain), min(len(X_domain), 10000), replace=False)
        scores = cross_val_score(clf, X_domain[idx], y_domain[idx], cv=3)
        domain_acc = scores.mean()
        
        # Save Domain Metrics
        domain_sep_metrics.append({
            "model": m_name, "seed": seed,
            "centroid_dist_src_tgt": dist_src_tgt,
            "domain_classifier_acc": domain_acc
        })
        
        # Save Class Metrics
        class_sep_metrics.append({
            "model": m_name, "seed": seed,
            "centroid_dist_src_benign_attack": dist_src_classes,
            "centroid_dist_tgt_benign_attack": dist_tgt_classes
        })
        
        # Score distribution
        score_dist_metrics.append({
            "model": m_name, "seed": seed,
            "tgt_benign_mean": prob_test[tgt_benign_idx].mean() if sum(tgt_benign_idx)>0 else 0,
            "tgt_benign_std": prob_test[tgt_benign_idx].std() if sum(tgt_benign_idx)>0 else 0,
            "tgt_attack_mean": prob_test[tgt_attack_idx].mean() if sum(tgt_attack_idx)>0 else 0,
            "tgt_attack_std": prob_test[tgt_attack_idx].std() if sum(tgt_attack_idx)>0 else 0,
        })
        
        # PCA for Seed 42
        if seed == 42:
            print(f"  Generating PCA for {m_name} (Seed 42)")
            pca = PCA(n_components=2)
            # Fit on combination of src and tgt
            feat_2d = pca.fit_transform(X_domain)
            
            val_2d = feat_2d[:len(feat_val)]
            tgt_2d = feat_2d[len(feat_val):]
            
            plt.figure(figsize=(10, 8))
            plt.scatter(val_2d[src_attack_idx, 0], val_2d[src_attack_idx, 1], c='red', alpha=0.1, label='Src Attack', s=5)
            plt.scatter(val_2d[src_benign_idx, 0], val_2d[src_benign_idx, 1], c='blue', alpha=0.1, label='Src Benign', s=5)
            plt.scatter(tgt_2d[tgt_attack_idx, 0], tgt_2d[tgt_attack_idx, 1], c='orange', alpha=0.5, label='Tgt Attack', s=10)
            plt.scatter(tgt_2d[tgt_benign_idx, 0], tgt_2d[tgt_benign_idx, 1], c='green', alpha=0.9, label='Tgt Benign', s=30, marker='x')
            plt.title(f"PCA Latent Representation: {m_name} (Seed 42)")
            plt.legend()
            plt.grid(True)
            plt.savefig(f"{out_dir}/pca_{m_name.lower().replace('-', '_')}.png")
            plt.close()

# Save aggregated
df_domain = pd.DataFrame(domain_sep_metrics)
df_domain.to_csv(f"{out_dir}/domain_separation_metrics.csv", index=False)
df_class = pd.DataFrame(class_sep_metrics)
df_class.to_csv(f"{out_dir}/class_separation_metrics.csv", index=False)
df_score = pd.DataFrame(score_dist_metrics)
df_score.to_csv(f"{out_dir}/score_distribution_metrics.csv", index=False)

df_seed = df_domain.merge(df_class, on=['model', 'seed']).merge(df_score, on=['model', 'seed'])
df_seed.to_csv(f"{out_dir}/latent_statistics.csv", index=False)

grouped = df_seed.groupby('model').agg(['mean', 'std']).reset_index()
grouped.columns = ['_'.join(col).strip() if col[1] else col[0] for col in grouped.columns.values]
grouped.to_csv(f"{out_dir}/seed_summary.csv", index=False)

with open(f"{out_dir}/config.json", "w") as f:
    json.dump({"run": "latent_analysis"}, f)
with open(f"{out_dir}/manifest.json", "w") as f:
    json.dump({"status": "complete"}, f)

print("Latent analysis metrics generated.")
