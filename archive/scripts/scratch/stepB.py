import pandas as pd

report = ["\n## B. TON_IoT (211,043 rows)"]
try:
    df = pd.read_csv("data/raw/ton_iot/train_test/Train_Test_Network_dataset/train_test_network.csv", usecols=['label', 'type'])
    label_counts = df['label'].value_counts(dropna=False).to_dict()
    type_counts = df['type'].value_counts(dropna=False).to_dict()
    
    report.append(f"**Benign Count (0):** {label_counts.get(0, 0):,}")
    report.append(f"**Attack Count (1):** {label_counts.get(1, 0):,}")
    
    report.append("\n**Attack-type distribution:**")
    for k, v in type_counts.items():
        report.append(f"- {k}: {v:,}")
        
    with open("reports/DG_DATA_AUDIT_addendum2.md", "a") as f:
        f.write("\n".join(report) + "\n")
    print("Step B complete")
except Exception as e:
    print(f"Error in Step B: {e}")
