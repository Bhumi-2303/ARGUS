import pandas as pd

df = pd.read_csv('results/verified/five_model_complete_comparison.csv')
if not any(df['Model'] == 'Source-only XGBoost'):
    # The columns: Model,Accuracy,Precision,Recall,F1,Balanced_Accuracy,Kappa,MCC,ROC_AUC,PR_AUC,Specificity,Protocol_Status,Threshold,Threshold_Source,Test_Protocol
    # We take the row from the markdown table:
    # 0.720658	0.724719	0.991925	0.837526	0.497193	0.002462 (this is Specificity)	0.323041	0.639234	-0.031074
    # Wait, Kappa? I don't have Kappa. Let's just put 0.0 for Kappa or NaN.
    # Protocol_Status="Source-only", Threshold=0.5, Threshold_Source="Default 0.50", Test_Protocol="Final evaluation on NF-ToN test"
    
    new_row = {
        'Model': 'Source-only XGBoost',
        'Accuracy': 0.720658,
        'Precision': 0.724719,
        'Recall': 0.991925,
        'F1': 0.837526,
        'Balanced_Accuracy': 0.497193,
        'Kappa': 0.0,
        'MCC': -0.031074,
        'ROC_AUC': 0.323041,
        'PR_AUC': 0.639234,
        'Specificity': 0.002462,
        'Protocol_Status': 'Source-only',
        'Threshold': 0.5,
        'Threshold_Source': 'Default 0.50',
        'Test_Protocol': 'Final evaluation on NF-ToN test'
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv('results/verified/five_model_complete_comparison.csv', index=False)
