import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, balanced_accuracy_score
import os

from model import V2TransformerClassifier

def extract_groups(df, domain):
    # Setup base tensors
    N = len(df)
    
    if domain == "ciciot":
        total_pkts = df['Number'].values
        rate = df['Rate'].values
        total_bytes = df['Tot sum'].values
        duration = total_pkts / np.maximum(rate, 1e-6)
        mean_pkt = df['AVG'].values
        max_pkt = df['Max'].values
        pkt_mean_to_max = np.where(max_pkt == 0, 0.0, mean_pkt / max_pkt)
        flag_cols = [c for c in df.columns if "flag" in c.lower()]
        tcp_flag_density = df[flag_cols].sum(axis=1).values if flag_cols else np.zeros(N)
        proto = df['Protocol Type'].values
        
        # Masking Directional (Token 4)
        dir_val = np.zeros((N, 2))
        # Mask shape: [N, 6]. CLS, Size, Vol, Proto, Dir, Time
        # PyTorch src_key_padding_mask: True means ignore
        mask = np.zeros((N, 6), dtype=bool)
        mask[:, 4] = True # Ignore Token 4 (Dir)
        
    elif domain == "nfton":
        duration = df['FLOW_DURATION_MILLISECONDS'].values / 1000.0
        in_p = df['IN_PKTS'].values
        out_p = df['OUT_PKTS'].values
        total_pkts = in_p + out_p
        
        in_b = df['IN_BYTES'].values
        out_b = df['OUT_BYTES'].values
        total_bytes = in_b + out_b
        
        mean_pkt = total_bytes / np.maximum(total_pkts, 1)
        pkt_mean_to_max = np.ones_like(mean_pkt)
        max_pkt = mean_pkt
        tcp_flag_density = df['TCP_FLAGS'].apply(lambda x: bin(x).count('1')).values
        proto = df['PROTOCOL'].values
        
        fwd_pkt_ratio = in_p / np.maximum(total_pkts, 1)
        fwd_byte_ratio = in_b / np.maximum(total_bytes, 1)
        dir_val = np.stack([fwd_pkt_ratio, fwd_byte_ratio], axis=1)
        
        mask = np.zeros((N, 6), dtype=bool) # All present
        
    elif domain == "bot":
        duration = df['dur'].values
        total_pkts = df['pkts'].values
        total_bytes = df['bytes'].values
        
        mean_pkt = total_bytes / np.maximum(total_pkts, 1)
        pkt_mean_to_max = np.ones_like(mean_pkt)
        max_pkt = mean_pkt
        tcp_flag_density = df.apply(lambda x: len(str(x['flgs'])) if x['proto'] == 'tcp' else 0, axis=1).values
        proto = np.zeros(N, dtype=int) # simplified proto id for plumbing
        
        spkts = df['spkts'].values
        sbytes = df['sbytes'].values
        fwd_pkt_ratio = spkts / np.maximum(total_pkts, 1)
        fwd_byte_ratio = sbytes / np.maximum(total_bytes, 1)
        dir_val = np.stack([fwd_pkt_ratio, fwd_byte_ratio], axis=1)
        
        mask = np.zeros((N, 6), dtype=bool)
        
    # Group 1: Size
    size_val = np.stack([np.log1p(mean_pkt), np.log1p(max_pkt), pkt_mean_to_max], axis=1)
    
    # Group 2: Volumetric
    vol_val = np.stack([np.log1p(total_pkts), np.log1p(total_bytes)], axis=1)
    
    # Group 3: Protocol (proto_id, tcp_density)
    proto_id = np.clip(proto, 0, 255).astype(np.int64)
    
    # Group 5: Timing
    time_val = np.stack([np.log1p(duration), np.log1p(total_bytes / np.maximum(duration, 0.001))], axis=1)
    
    # Prepare Dict
    return {
        'size': torch.FloatTensor(size_val),
        'vol': torch.FloatTensor(vol_val),
        'proto_id': torch.LongTensor(proto_id),
        'tcp_density': torch.FloatTensor(tcp_flag_density),
        'dir': torch.FloatTensor(dir_val),
        'time': torch.FloatTensor(time_val),
        'key_padding_mask': torch.BoolTensor(mask)
    }

def train_model(X, y, epochs=5, lr=1e-3, seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Split: 60/20/20
    idx = np.arange(len(y))
    idx_train, idx_temp, y_train, y_temp = train_test_split(idx, y, test_size=0.4, random_state=seed, stratify=y)
    idx_val, idx_test, y_val, y_test = train_test_split(idx_temp, y_temp, test_size=0.5, random_state=seed, stratify=y_temp)
    
    model = V2TransformerClassifier(d_model=32, nhead=4, num_layers=2)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    
    batch_size = 256
    
    def get_batch(idx_list):
        return {k: v[idx_list] for k, v in X.items()}, torch.LongTensor(y[idx_list])
    
    for ep in range(epochs):
        model.train()
        np.random.shuffle(idx_train)
        
        for i in range(0, len(idx_train), batch_size):
            b_idx = idx_train[i:i+batch_size]
            b_X, b_y = get_batch(b_idx)
            
            optimizer.zero_grad()
            logits = model(b_X)
            loss = criterion(logits, b_y)
            loss.backward()
            optimizer.step()
            
    # Eval on Test
    model.eval()
    with torch.no_grad():
        t_X, t_y = get_batch(idx_test)
        logits = model(t_X)
        probs = torch.softmax(logits, dim=1)[:, 1].numpy()
        preds = np.argmax(logits.numpy(), axis=1)
        
        acc = accuracy_score(t_y.numpy(), preds)
        auc = roc_auc_score(t_y.numpy(), probs)
        bacc = balanced_accuracy_score(t_y.numpy(), preds)
        
    return model, acc, auc, bacc

if __name__ == "__main__":
    print("Loading data for plumbing test (100k samples max per domain for speed)...")
    # CICIoT
    df_cic = pd.read_csv("../../../data/raw/cic_iot_2023/raw/CSV/MERGED_CSV/Merged01.csv", nrows=700000).sample(n=100000, random_state=42)
    # Define labels (binary)
    y_cic = (df_cic['Label'] != 'BenignTraffic').astype(int).values
    X_cic = extract_groups(df_cic, "ciciot")
    
    # NF-ToN
    df_nf = pd.read_parquet("../../../data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet").head(100000)
    y_nf = df_nf['Label'].values
    X_nf = extract_groups(df_nf, "nfton")
    
    print("Training CICIoT Model...")
    model_cic, cic_acc, cic_auc, cic_bacc = train_model(X_cic, y_cic, seed=42)
    print(f"CICIoT In-Domain (Test) -> Acc: {cic_acc:.4f}, B.Acc: {cic_bacc:.4f}, AUC: {cic_auc:.4f}")
    
    print("\nTraining NF-ToN Model...")
    model_nf, nf_acc, nf_auc, nf_bacc = train_model(X_nf, y_nf, seed=42)
    print(f"NF-ToN In-Domain (Test) -> Acc: {nf_acc:.4f}, B.Acc: {nf_bacc:.4f}, AUC: {nf_auc:.4f}")
    
    print("\nCross-Evaluating...")
    model_cic.eval()
    with torch.no_grad():
        logits_x1 = model_cic(X_nf)
        preds_x1 = np.argmax(logits_x1.numpy(), axis=1)
        x1_bacc = balanced_accuracy_score(y_nf, preds_x1)
        print(f"Model: CICIoT -> Test: NF-ToN -> B.Acc: {x1_bacc:.4f}")
        
    model_nf.eval()
    with torch.no_grad():
        logits_x2 = model_nf(X_cic)
        preds_x2 = np.argmax(logits_x2.numpy(), axis=1)
        x2_bacc = balanced_accuracy_score(y_cic, preds_x2)
        print(f"Model: NF-ToN -> Test: CICIoT -> B.Acc: {x2_bacc:.4f}")

    print("\nMasking Sanity Check on BoT-IoT...")
    df_bot = pd.read_csv("../../../scratch/BoT-IoT dataset/csv/data_32.csv", nrows=1000, low_memory=False)
    X_bot = extract_groups(df_bot, "bot")
    try:
        model_cic.eval()
        with torch.no_grad():
            out_bot = model_cic(X_bot)
        print("BoT-IoT Passed through CICIoT model successfully! Output shape:", out_bot.shape)
    except Exception as e:
        print("BoT-IoT Masking Test Failed:", e)

