import os
import time
import json
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import shap

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, balanced_accuracy_score,
    matthews_corrcoef, cohen_kappa_score, log_loss,
    confusion_matrix, classification_report
)
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier

import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, CSVLogger, ModelCheckpoint
import optuna

plt.switch_backend('Agg')

def parse_args():
    parser = argparse.ArgumentParser(description="ARGUS Phase 3: Multi-Dataset Training")
    parser.add_argument("--train-dataset", type=str, required=True, help="Dataset to train on")
    parser.add_argument("--test-dataset", type=str, required=True, help="Dataset to test on")
    parser.add_argument("--trials", type=int, default=50, help="Number of Optuna trials")
    return parser.parse_args()

def setup_directories(train_ds: str, test_ds: str):
    exp_dir = Path(f"training/exports/exp_{train_ds}_{test_ds}")
    dirs = {
        "models": exp_dir / "models",
        "reports": exp_dir / "reports",
        "figures": exp_dir / "reports/figures",
        "best": Path("training/models/best")
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs

def load_data(dataset: str):
    data_dir = Path(f"training/data/processed/{dataset}")
    if not data_dir.exists():
        raise FileNotFoundError(f"Processed data for {dataset} not found. Run Phase 2 first.")
    
    train_df = pd.read_parquet(data_dir / "training.parquet")
    val_df = pd.read_parquet(data_dir / "validation.parquet")
    test_df = pd.read_parquet(data_dir / "testing.parquet")
    
    return train_df, val_df, test_df

def align_features(train_df, test_df):
    """Align test features to train features if evaluating cross-dataset."""
    train_features = [c for c in train_df.columns if c != 'Label']
    
    X_test = pd.DataFrame()
    for col in train_features:
        if col in test_df.columns:
            X_test[col] = test_df[col]
        else:
            X_test[col] = 0
            
    y_test = test_df['Label'] if 'Label' in test_df.columns else np.zeros(len(test_df))
    return X_test, y_test

def evaluate_model(model_name, y_true, y_pred, y_prob, train_time, infer_time, reports_dir):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_true, y_pred, average='macro', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)
    
    roc_auc = roc_auc_score(y_true, y_prob) if y_prob is not None else 0
    pr_auc = average_precision_score(y_true, y_prob) if y_prob is not None else 0
    
    bal_acc = balanced_accuracy_score(y_true, y_pred)
    mcc = matthews_corrcoef(y_true, y_pred)
    kappa = cohen_kappa_score(y_true, y_pred)
    ll = log_loss(y_true, y_prob) if y_prob is not None else 0
    
    metrics = {
        "Accuracy": acc, "Precision": prec, "Recall": rec, "F1": f1,
        "ROC_AUC": roc_auc, "PR_AUC": pr_auc, "Balanced_Accuracy": bal_acc,
        "Matthews_Correlation": mcc, "Cohen_Kappa": kappa, "Log_Loss": ll,
        "Training_Time_s": train_time, "Inference_Time_s": infer_time
    }
    
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = confusion_matrix(y_true, y_pred, normalize='true')
    
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax[0])
    ax[0].set_title(f"{model_name} Raw Confusion Matrix")
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', ax=ax[1])
    ax[1].set_title(f"{model_name} Normalized Confusion Matrix")
    for ext in ['png', 'svg', 'pdf']:
        plt.savefig(reports_dir / f"figures/{model_name}_cm.{ext}", dpi=300, bbox_inches='tight')
    plt.close()
    
    return metrics

def train_optuna_tree(model_class, model_name, X_train, y_train, trials_count):
    print(f"[*] Tuning {model_name}...")
    
    def objective(trial):
        if model_name == "Random Forest":
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 5, 30),
                'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
                'n_jobs': -1, 'random_state': 42
            }
            model = RandomForestClassifier(**params)
        elif model_name == "XGBoost":
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
                'n_jobs': -1, 'random_state': 42, 'use_label_encoder': False, 'eval_metric': 'logloss'
            }
            model = xgb.XGBClassifier(**params)
        elif model_name == "LightGBM":
            params = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 15),
                'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
                'n_jobs': -1, 'random_state': 42, 'verbose': -1
            }
            model = lgb.LGBMClassifier(**params)
        elif model_name == "CatBoost":
            params = {
                'iterations': trial.suggest_int('iterations', 50, 300),
                'depth': trial.suggest_int('depth', 4, 10),
                'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
                'random_seed': 42, 'verbose': 0
            }
            model = CatBoostClassifier(**params)
            
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_va = y_train.iloc[train_idx], y_train.iloc[val_idx]
            model.fit(X_tr, y_tr)
            preds = model.predict(X_va)
            scores.append(f1_score(y_va, preds, average='macro'))
            
        return np.mean(scores)
        
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=trials_count)
    return study.best_params

def train_neural_network(X_train, y_train, X_val, y_val, models_dir, reports_dir):
    print("[*] Training TensorFlow Neural Network...")
    model = Sequential([
        Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
        BatchNormalization(),
        Dropout(0.3),
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', tf.keras.metrics.Precision(name='precision'), tf.keras.metrics.Recall(name='recall')])
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        CSVLogger(reports_dir / 'NN_History.csv'),
        ModelCheckpoint(filepath=str(models_dir / 'NN_model.keras'), save_best_only=True)
    ]
    
    start_time = time.time()
    history = model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=256, callbacks=callbacks, verbose=1)
    train_time = time.time() - start_time
    
    model.save(models_dir / 'NN_model.h5')
    
    hist_df = pd.DataFrame(history.history)
    hist_df.to_excel(reports_dir / 'NN_History.xlsx', index=False)
    
    for metric in ['loss', 'accuracy', 'precision', 'recall']:
        cols = [c for c in hist_df.columns if metric in c]
        if cols:
            plt.figure()
            hist_df[cols].plot()
            plt.title(f"NN {metric.capitalize()} Curve")
            plt.savefig(reports_dir / f"figures/NN_{metric}_curve.png")
            plt.close()
            
    return model, train_time

def main():
    args = parse_args()
    print(f"=== Phase 3: Train {args.train_dataset} -> Test {args.test_dataset} ===")
    
    dirs = setup_directories(args.train_dataset, args.test_dataset)
    
    print("[*] Loading datasets...")
    train_df, val_df, _ = load_data(args.train_dataset)
    _, _, test_df = load_data(args.test_dataset)
    
    y_train = train_df['Label']
    X_train = train_df.drop(columns=['Label'])
    
    y_val = val_df['Label']
    X_val = val_df.drop(columns=['Label'])
    
    X_test, y_test = align_features(X_train, test_df)
    
    models_to_train = [
        ("Random Forest", RandomForestClassifier),
        ("XGBoost", xgb.XGBClassifier),
        ("LightGBM", lgb.LGBMClassifier),
        ("CatBoost", CatBoostClassifier)
    ]
    
    all_metrics = {}
    
    for name, model_class in models_to_train:
        print(f"\n[*] --- {name} ---")
        best_params = train_optuna_tree(model_class, name, X_train, y_train, args.trials)
        with open(dirs["models"] / f"{name}_hyperparameters.json", "w") as f:
            json.dump(best_params, f, indent=4)
            
        model = model_class(**best_params)
        
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        start_time = time.time()
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
        infer_time = time.time() - start_time
        
        metrics = evaluate_model(name, y_test, y_pred, y_prob, train_time, infer_time, dirs["reports"])
        all_metrics[name] = metrics
        
        if name == "Random Forest":
            joblib.dump(model, dirs["models"] / f"{name}.joblib")
        elif name == "XGBoost":
            model.save_model(dirs["models"] / f"{name}.json")
        elif name == "LightGBM":
            model.booster_.save_model(dirs["models"] / f"{name}.txt")
        elif name == "CatBoost":
            model.save_model(dirs["models"] / f"{name}.cbm")
            
        try:
            print(f"[*] Generating SHAP for {name}...")
            X_sample = X_test.sample(min(1000, len(X_test)))
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
            
            plt.figure()
            shap.summary_plot(shap_values, X_sample, show=False)
            plt.savefig(dirs["figures"] / f"{name}_shap_summary.png", bbox_inches='tight')
            plt.close()
            
            plt.figure()
            shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
            plt.savefig(dirs["figures"] / f"{name}_shap_bar.png", bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"[!] SHAP generation failed for {name}: {e}")

    print("\n[*] --- Neural Network ---")
    nn_model, nn_train_time = train_neural_network(X_train, y_train, X_val, y_val, dirs["models"], dirs["reports"])
    
    start_time = time.time()
    nn_prob = nn_model.predict(X_test).flatten()
    nn_pred = (nn_prob > 0.5).astype(int)
    nn_infer_time = time.time() - start_time
    
    nn_metrics = evaluate_model("Neural Network", y_test, nn_pred, nn_prob, nn_train_time, nn_infer_time, dirs["reports"])
    all_metrics["Neural Network"] = nn_metrics
    
    df_metrics = pd.DataFrame.from_dict(all_metrics, orient='index')
    df_metrics.to_csv(dirs["reports"] / "leaderboard.csv")
    df_metrics.to_excel(dirs["reports"] / "leaderboard.xlsx")
    df_metrics.to_html(dirs["reports"] / "leaderboard.html")
    df_metrics.to_markdown(dirs["reports"] / "leaderboard.md")
    
    with open(dirs["reports"] / "metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=4)
        
    print("\n[*] Leaderboard:")
    print(df_metrics[['F1', 'ROC_AUC', 'Balanced_Accuracy']])
    
    best_model_name = df_metrics['F1'].idxmax()
    print(f"\n[*] Best Model: {best_model_name}")
    with open(dirs["best"] / f"best_model_exp_{args.train_dataset}_{args.test_dataset}.txt", "w") as f:
        f.write(f"Best Model for {args.train_dataset} -> {args.test_dataset}: {best_model_name}\n")
        
    print("=== Phase 3 Execution Complete ===")

if __name__ == "__main__":
    main()
