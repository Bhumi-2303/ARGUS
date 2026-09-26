import pandas as pd

# D1 -> D2 DANN predictions
dann_file = 'ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_final_test_predictions.csv'
df = pd.read_csv(dann_file)

# Rename columns to match the required format
df_out = pd.DataFrame({
    'sample_index': range(len(df)),
    'true_label': df['label'],
    'predicted_probability': df['probability']
})

out_file = 'ARGUS_Cross_Domain_Results/argus_coral_data/dann_results/dann_d1_to_d2_raw_predictions.csv'
df_out.to_csv(out_file, index=False)
print(f"Saved DANN formatted predictions to {out_file}")

