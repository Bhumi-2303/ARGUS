import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import balanced_accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
import sys
sys.path.append("src/argus/v2_transformer")
from model import V2TransformerClassifier
from train_plumbing import extract_groups, train_model

def get_embeddings(model, X_dict, batch_size=256):
    model.eval()
    all_cls = []
    N = X_dict['size'].shape[0]
    with torch.no_grad():
        for i in range(0, N, batch_size):
            b_X = {k: v[i:i+batch_size] for k, v in X_dict.items()}
            # get CLS from transformer
            tokens = model.embedder(
                b_X['size'], b_X['vol'], b_X['proto_id'], 
                b_X['tcp_density'], b_X['dir'], b_X['time']
            )
            mask = b_X.get('key_padding_mask', None)
            out = model.transformer(tokens, src_key_padding_mask=mask)
            cls_out = out[:, 0, :]
            all_cls.append(cls_out.cpu().numpy())
    return np.concatenate(all_cls, axis=0)

print("Loading data...")
df_cic = pd.read_csv("data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv", nrows=100000)
y_cic = (df_cic['Label'] != 'BenignTraffic').astype(int).values
X_cic = extract_groups(df_cic, "ciciot")

df_nf = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet").head(100000)
y_nf = df_nf['Label'].values
X_nf = extract_groups(df_nf, "nfton")

df_bot = pd.read_csv("scratch/BoT-IoT dataset/csv/data_32.csv", nrows=100000, low_memory=False)
X_bot = extract_groups(df_bot, "bot")

# --- Step 3: Seed Stability ---
print("--- Cross-Domain Seed Stability ---")
seeds = [42, 123, 456]
cic_to_nf_bacc = []
nf_to_cic_bacc = []

saved_model = None

for seed in seeds:
    print(f"Training Seed {seed}...")
    model_cic, _, _, _ = train_model(X_cic, y_cic, seed=seed)
    model_nf, _, _, _ = train_model(X_nf, y_nf, seed=seed)
    
    if seed == 42:
        saved_model = model_cic # Keep for embedding extraction
        
    model_cic.eval()
    with torch.no_grad():
        logits = model_cic(X_nf)
        bacc1 = balanced_accuracy_score(y_nf, np.argmax(logits.numpy(), axis=1))
        cic_to_nf_bacc.append(bacc1)
        
    model_nf.eval()
    with torch.no_grad():
        logits = model_nf(X_cic)
        bacc2 = balanced_accuracy_score(y_cic, np.argmax(logits.numpy(), axis=1))
        nf_to_cic_bacc.append(bacc2)
        
print(f"CICIoT -> NF-ToN B.Acc: {np.mean(cic_to_nf_bacc):.4f} +/- {np.std(cic_to_nf_bacc):.4f}")
print(f"NF-ToN -> CICIoT B.Acc: {np.mean(nf_to_cic_bacc):.4f} +/- {np.std(nf_to_cic_bacc):.4f}")

# --- Step 1: Domain Separability on Embeddings ---
print("\n--- Domain Separability on Learned Embeddings ---")
emb_cic = get_embeddings(saved_model, X_cic)
emb_nf = get_embeddings(saved_model, X_nf)
emb_bot = get_embeddings(saved_model, X_bot)

min_len = 30000
# Pairwise: CICIoT vs NF-ToN
X_pair = np.vstack([emb_cic[:min_len], emb_nf[:min_len]])
y_pair = np.array([0]*min_len + [1]*min_len)

clf = RandomForestClassifier(n_estimators=20, max_depth=5, random_state=42)
scores_pair = cross_val_score(clf, X_pair, y_pair, cv=3)
acc_pair = np.mean(scores_pair)
print(f"Pairwise Domain Separability (CICIoT vs NF-ToN): {acc_pair:.4f}")

# 3-Way: CICIoT vs NF-ToN vs BoT-IoT
X_3way = np.vstack([emb_cic[:min_len], emb_nf[:min_len], emb_bot[:min_len]])
y_3way = np.array([0]*min_len + [1]*min_len + [2]*min_len)

scores_3way = cross_val_score(clf, X_3way, y_3way, cv=3)
acc_3way = np.mean(scores_3way)
print(f"3-Way Domain Separability: {acc_3way:.4f}")


# --- Step 2: Per-Domain Diversity (Effective Unique Vectors) ---
print("\n--- Effective Unique Vectors (Rounding to 2 decimals) ---")
for name, emb in [("CICIoT", emb_cic), ("NF-ToN", emb_nf), ("BoT-IoT", emb_bot)]:
    rounded = np.round(emb[:min_len], decimals=2)
    unique = len(np.unique(rounded, axis=0))
    print(f"{name} Effective Diversity: {unique} / {min_len} ({unique/min_len*100:.2f}%)")

