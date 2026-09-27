import pandas as pd
import numpy as np

ciciot = pd.read_csv("data/raw/cic_iot_2023/processed/part-00000-363d1ba3-8ab5-4f96-bc25-4d5862db7cb9-c000.csv", nrows=100000)
nfton = pd.read_parquet("data/raw/nf_ton_iot/processed/NF-ToN-IoT.parquet").head(100000)
bot = pd.read_csv("data/raw/bot_iot/raw/BoT-IoT dataset/csv/data_32.csv", nrows=100000, low_memory=False)

protocol_map = {6: 'TCP', 17: 'UDP', 1: 'ICMP', 2054: 'ARP', 58: 'IPv6-ICMP'}
def map_bot_proto(p):
    p = str(p).lower()
    if p == 'tcp': return 'TCP'
    if p == 'udp': return 'UDP'
    if p == 'icmp': return 'ICMP'
    if p == 'arp': return 'ARP'
    if p == 'ipv6-icmp': return 'IPv6-ICMP'
    return 'Other'

def get_v2(ciciot, nfton, bot):
    df_cic = pd.DataFrame()
    df_cic['duration'] = ciciot['flow_duration']
    df_cic['total_pkts'] = ciciot['Number']
    df_cic['total_bytes'] = ciciot['Tot sum']
    df_cic['protocol'] = ciciot['Protocol Type'].map(protocol_map).fillna('Other')
    df_cic['bytes_per_packet'] = df_cic['total_bytes'] / np.maximum(df_cic['total_pkts'], 1)
    df_cic['packet_rate'] = df_cic['total_pkts'] / np.maximum(df_cic['duration'], 0.001)
    df_cic['byte_rate'] = df_cic['total_bytes'] / np.maximum(df_cic['duration'], 0.001)
    df_cic['label'] = (ciciot['label'] != 'BenignTraffic').astype(int)
    
    df_nft = pd.DataFrame()
    df_nft['duration'] = nfton['FLOW_DURATION_MILLISECONDS'] / 1000.0
    df_nft['total_pkts'] = nfton['IN_PKTS'] + nfton['OUT_PKTS']
    df_nft['total_bytes'] = nfton['IN_BYTES'] + nfton['OUT_BYTES']
    df_nft['protocol'] = nfton['PROTOCOL'].map(protocol_map).fillna('Other')
    df_nft['bytes_per_packet'] = df_nft['total_bytes'] / np.maximum(df_nft['total_pkts'], 1)
    df_nft['packet_rate'] = df_nft['total_pkts'] / np.maximum(df_nft['duration'], 0.001)
    df_nft['byte_rate'] = df_nft['total_bytes'] / np.maximum(df_nft['duration'], 0.001)
    df_nft['label'] = (nfton['Label'] == 1).astype(int)
    
    df_bot = pd.DataFrame()
    df_bot['duration'] = bot['dur']
    df_bot['total_pkts'] = bot['pkts']
    df_bot['total_bytes'] = bot['bytes']
    df_bot['protocol'] = bot['proto'].apply(map_bot_proto)
    df_bot['bytes_per_packet'] = df_bot['total_bytes'] / np.maximum(df_bot['total_pkts'], 1)
    df_bot['packet_rate'] = df_bot['total_pkts'] / np.maximum(df_bot['duration'], 0.001)
    df_bot['byte_rate'] = df_bot['total_bytes'] / np.maximum(df_bot['duration'], 0.001)
    df_bot['label'] = (bot['attack'] == 1).astype(int)
    
    return df_cic, df_nft, df_bot

df_cic, df_nft, df_bot = get_v2(ciciot, nfton, bot)
v2_cols = ['duration', 'total_pkts', 'total_bytes', 'protocol', 'bytes_per_packet', 'packet_rate', 'byte_rate']

print("--- V2 Class Distributions (Deduplicated) ---")
for name, df in [("CICIoT", df_cic), ("NF-ToN", df_nft), ("BoT-IoT", df_bot)]:
    dd = df.drop_duplicates(subset=v2_cols)
    total = len(dd)
    atk = dd['label'].sum()
    ben = total - atk
    print(f"{name}: Total {total} | Benign {ben} | Attack {atk} | Prevalence {atk/total*100:.1f}%")

