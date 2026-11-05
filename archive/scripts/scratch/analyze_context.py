import pandas as pd

for domain in [('CICIoT2023', 'data/raw/legacy_package/argus_coral_data/ciciot_test_features.csv'), 
               ('NF-ToN-IoT-v2', 'data/raw/legacy_package/argus_coral_data/nfton_test_features.csv')]:
    df = pd.read_csv(domain[1])
    feats = df[['pkt_mean_to_max', 'tcp_flag_density', 'log_pkt_mean', 'log_pkt_max']]
    unique_count = feats.drop_duplicates().shape[0]
    total_count = feats.shape[0]
    print(f"{domain[0]} unique vectors: {unique_count} out of {total_count} ({unique_count/total_count*100:.2f}%)")

