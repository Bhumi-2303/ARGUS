import os
import gc
import json
import time
import psutil
import shutil
import logging
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             roc_auc_score, average_precision_score, balanced_accuracy_score,
                             matthews_corrcoef, cohen_kappa_score, log_loss,
                             confusion_matrix, roc_curve, precision_recall_curve)
from sklearn.model_selection import StratifiedKFold
import joblib

import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier, Pool

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, BatchNormalization, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, CSVLogger, TensorBoard

import optuna
import shap

warnings.filterwarnings('ignore')

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
PROCESSED_DATA_DIR = Path("training/data/processed")
REPORTS_DIR = Path("training/reports")
MODELS_DIR = Path("training/exports")
BEST_MODEL_DIR = Path("models/best_model")

for d in [REPORTS_DIR, MODELS_DIR, BEST_MODEL_DIR]:
    d.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "shap").mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "figures").mkdir(parents=True, exist_ok=True)
    
logging.basicConfig(level=logging.INFO, format='[*] %(message)s')

# -------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------
def get_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 ** 2) # in MB

def clear_memory():
    gc.collect()

def load_processed_data():
    logging.info("Loading processed datasets...")
    # Support both Parquet and CSV
    train_path_pq = PROCESSED_DATA_DIR / "training.parquet"
    train_path_csv = PROCESSED_DATA_DIR / "training.csv"
    
    if train_path_pq.exists():
        train_df = pd.read_parquet(train_path_pq)
        val_df = pd.read_parquet(PROCESSED_DATA_DIR / "validation.parquet")
        test_df = pd.read_parquet(PROCESSED_DATA_DIR / "testing.parquet")
    else:
        train_df = pd.read_csv(train_path_csv, low_memory=False)
        val_df = pd.read_csv(PROCESSED_DATA_DIR / "validation.csv", low_memory=False)
        test_df = pd.read_csv(PROCESSED_DATA_DIR / "testing.csv", low_memory=False)

    # Assuming 'Label' is the target column from Phase 2
    target_col = 'Label' 
    X_train = train_df.drop(columns=[target_col])
    y_train = train_df[target_col]
    
    X_val = val_df.drop(columns=[target_col])
    y_val = val_df[target_col]
    
    X_test = test_df.drop(columns=[target_col])
    y_test = test_df[target_col]
    
    logging.info(f"Train shape: {X_train.shape}, Val shape: {X_val.shape}, Test shape: {X_test.shape}")
    return X_train, y_train, X_val, y_val, X_test, y_test

def evaluate_model(y_true, y_pred, y_prob, model_name, train_time, inf_time, mem_usage):
    metrics = {
        'Model': model_name,
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, zero_division=0, average='binary'),
        'Recall': recall_score(y_true, y_pred, zero_division=0, average='binary'),
        'F1 Score': f1_score(y_true, y_pred, zero_division=0, average='binary'),
        'ROC AUC': roc_auc_score(y_true, y_prob) if y_prob is not None else np.nan,
        'PR AUC': average_precision_score(y_true, y_prob) if y_prob is not None else np.nan,
        'Balanced Accuracy': balanced_accuracy_score(y_true, y_pred),
        'MCC': matthews_corrcoef(y_true, y_pred),
        'Cohen Kappa': cohen_kappa_score(y_true, y_pred),
        'Log Loss': log_loss(y_true, y_prob) if y_prob is not None else np.nan,
        'Training Time (s)': train_time,
        'Inference Time (s)': inf_time,
        'Memory Usage (MB)': mem_usage
    }
    return metrics

def plot_and_save(fig, filename):
    for fmt in ['png', 'svg', 'pdf']:
        fig.savefig(REPORTS_DIR / "figures" / f"{filename}.{fmt}", format=fmt, dpi=300, bbox_inches='tight')
    plt.close(fig)

def generate_visualizations(y_true, y_pred, y_prob, model_name):
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_title(f'{model_name} - Confusion Matrix')
    plot_and_save(fig, f"{model_name}_confusion_matrix")
    
    # Normalized Confusion Matrix
    cm_norm = confusion_matrix(y_true, y_pred, normalize='true')
    fig, ax = plt.subplots(figsize=(6,5))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', ax=ax)
    ax.set_title(f'{model_name} - Normalized Confusion Matrix')
    plot_and_save(fig, f"{model_name}_norm_confusion_matrix")
    
    if y_prob is not None:
        # ROC Curve
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        fig, ax = plt.subplots(figsize=(6,5))
        ax.plot(fpr, tpr, color='blue', label=f'AUC = {roc_auc_score(y_true, y_prob):.4f}')
        ax.plot([0, 1], [0, 1], color='red', linestyle='--')
        ax.set_title(f'{model_name} - ROC Curve')
        ax.legend()
        plot_and_save(fig, f"{model_name}_roc_curve")
        
        # PR Curve
        prec, rec, _ = precision_recall_curve(y_true, y_prob)
        fig, ax = plt.subplots(figsize=(6,5))
        ax.plot(rec, prec, color='blue', label=f'PR AUC = {average_precision_score(y_true, y_prob):.4f}')
        ax.set_title(f'{model_name} - Precision Recall Curve')
        ax.legend()
        plot_and_save(fig, f"{model_name}_pr_curve")

def run_shap_analysis(model, X_sample, model_name):
    try:
        if model_name == 'Neural Network':
            explainer = shap.DeepExplainer(model, X_sample.values)
            shap_values = explainer.shap_values(X_sample.values)
        elif model_name in ['Random Forest', 'XGBoost', 'LightGBM', 'CatBoost']:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample)
        else:
            return

        fig = plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_sample, show=False)
        plot_and_save(fig, f"{model_name}_shap_summary")
        
        fig = plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_sample, plot_type="bar", show=False)
        plot_and_save(fig, f"{model_name}_shap_bar")
        
    except Exception as e:
        logging.error(f"SHAP generation failed for {model_name}: {e}")

# -------------------------------------------------------------------
# Model Training Routines
# -------------------------------------------------------------------

def train_random_forest(X_train, y_train, X_val, y_val, X_test, y_test):
    logging.info("--- Training Random Forest ---")
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300),
            'max_depth': trial.suggest_int('max_depth', 5, 30),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'criterion': trial.suggest_categorical('criterion', ['gini', 'entropy']),
            'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
            'n_jobs': -1,
            'random_state': 42
        }
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_va = y_train.iloc[train_idx], y_train.iloc[val_idx]
            model = RandomForestClassifier(**params)
            model.fit(X_tr, y_tr)
            preds = model.predict(X_va)
            scores.append(f1_score(y_va, preds, zero_division=0, average='binary'))
        return np.mean(scores)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=5) # Reduced for testing, should be 100 for prod
    
    best_params = study.best_params
    logging.info(f"Best RF Params: {best_params}")
    
    t0 = time.time()
    best_model = RandomForestClassifier(**best_params, n_jobs=-1, random_state=42)
    best_model.fit(X_train, y_train)
    t_train = time.time() - t0
    
    t0 = time.time()
    preds = best_model.predict(X_test)
    probs = best_model.predict_proba(X_test)[:, 1]
    t_inf = time.time() - t0
    
    mem = get_memory_usage()
    
    metrics = evaluate_model(y_test, preds, probs, 'Random Forest', t_train, t_inf, mem)
    generate_visualizations(y_test, preds, probs, 'Random Forest')
    run_shap_analysis(best_model, X_train.sample(min(1000, len(X_train))), 'Random Forest')
    
    joblib.dump(best_model, MODELS_DIR / 'random_forest.joblib')
    return metrics, study, best_model

def train_xgboost(X_train, y_train, X_val, y_val, X_test, y_test):
    logging.info("--- Training XGBoost ---")
    def objective(trial):
        params = {
            'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'n_estimators': trial.suggest_int('n_estimators', 100, 500),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'lambda': trial.suggest_float('lambda', 1e-3, 10.0, log=True),
            'alpha': trial.suggest_float('alpha', 1e-3, 10.0, log=True),
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'tree_method': 'hist',
            'random_state': 42
        }
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_va = y_train.iloc[train_idx], y_train.iloc[val_idx]
            model = xgb.XGBClassifier(**params, early_stopping_rounds=20)
            model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], verbose=False)
            preds = model.predict(X_va)
            scores.append(f1_score(y_va, preds, zero_division=0, average='binary'))
        return np.mean(scores)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=5) # Reduced for testing, should be 100
    
    best_params = study.best_params
    best_params.update({'objective': 'binary:logistic', 'eval_metric': 'logloss', 'tree_method': 'hist'})
    
    t0 = time.time()
    best_model = xgb.XGBClassifier(**best_params, random_state=42)
    best_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    t_train = time.time() - t0
    
    t0 = time.time()
    preds = best_model.predict(X_test)
    probs = best_model.predict_proba(X_test)[:, 1]
    t_inf = time.time() - t0
    
    metrics = evaluate_model(y_test, preds, probs, 'XGBoost', t_train, t_inf, get_memory_usage())
    generate_visualizations(y_test, preds, probs, 'XGBoost')
    run_shap_analysis(best_model, X_train.sample(min(1000, len(X_train))), 'XGBoost')
    
    best_model.save_model(MODELS_DIR / 'xgboost.json')
    return metrics, study, best_model

def train_lightgbm(X_train, y_train, X_val, y_val, X_test, y_test):
    logging.info("--- Training LightGBM ---")
    def objective(trial):
        params = {
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
            'feature_fraction': trial.suggest_float('feature_fraction', 0.5, 1.0),
            'bagging_fraction': trial.suggest_float('bagging_fraction', 0.5, 1.0),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
            'lambda_l1': trial.suggest_float('lambda_l1', 1e-3, 10.0, log=True),
            'lambda_l2': trial.suggest_float('lambda_l2', 1e-3, 10.0, log=True),
            'objective': 'binary',
            'metric': 'binary_logloss',
            'random_state': 42,
            'verbose': -1
        }
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_va = y_train.iloc[train_idx], y_train.iloc[val_idx]
            model = lgb.LGBMClassifier(**params, n_estimators=100)
            model.fit(X_tr, y_tr, eval_set=[(X_va, y_va)], callbacks=[lgb.early_stopping(20, verbose=False)])
            preds = model.predict(X_va)
            scores.append(f1_score(y_va, preds, zero_division=0, average='binary'))
        return np.mean(scores)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=5)
    
    best_params = study.best_params
    best_params.update({'objective': 'binary', 'metric': 'binary_logloss', 'verbose': -1})
    
    t0 = time.time()
    best_model = lgb.LGBMClassifier(**best_params, n_estimators=100)
    best_model.fit(X_train, y_train, eval_set=[(X_val, y_val)], callbacks=[lgb.early_stopping(20, verbose=False)])
    t_train = time.time() - t0
    
    t0 = time.time()
    preds = best_model.predict(X_test)
    probs = best_model.predict_proba(X_test)[:, 1]
    t_inf = time.time() - t0
    
    metrics = evaluate_model(y_test, preds, probs, 'LightGBM', t_train, t_inf, get_memory_usage())
    generate_visualizations(y_test, preds, probs, 'LightGBM')
    run_shap_analysis(best_model, X_train.sample(min(1000, len(X_train))), 'LightGBM')
    
    best_model.booster_.save_model(str(MODELS_DIR / 'lightgbm.txt'))
    return metrics, study, best_model

def train_catboost(X_train, y_train, X_val, y_val, X_test, y_test):
    logging.info("--- Training CatBoost ---")
    def objective(trial):
        params = {
            'depth': trial.suggest_int('depth', 4, 10),
            'iterations': trial.suggest_int('iterations', 100, 500),
            'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
            'border_count': trial.suggest_int('border_count', 32, 255),
            'loss_function': 'Logloss',
            'verbose': False,
            'random_seed': 42
        }
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = []
        for train_idx, val_idx in skf.split(X_train, y_train):
            X_tr, X_va = X_train.iloc[train_idx], X_train.iloc[val_idx]
            y_tr, y_va = y_train.iloc[train_idx], y_train.iloc[val_idx]
            model = CatBoostClassifier(**params)
            model.fit(X_tr, y_tr, eval_set=(X_va, y_va), early_stopping_rounds=20)
            preds = model.predict(X_va)
            scores.append(f1_score(y_va, preds, zero_division=0, average='binary'))
        return np.mean(scores)

    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=5)
    
    best_params = study.best_params
    best_params.update({'loss_function': 'Logloss', 'verbose': False})
    
    t0 = time.time()
    best_model = CatBoostClassifier(**best_params)
    best_model.fit(X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=20)
    t_train = time.time() - t0
    
    t0 = time.time()
    preds = best_model.predict(X_test)
    probs = best_model.predict_proba(X_test)[:, 1]
    t_inf = time.time() - t0
    
    metrics = evaluate_model(y_test, preds, probs, 'CatBoost', t_train, t_inf, get_memory_usage())
    generate_visualizations(y_test, preds, probs, 'CatBoost')
    run_shap_analysis(best_model, X_train.sample(min(1000, len(X_train))), 'CatBoost')
    
    best_model.save_model(str(MODELS_DIR / 'catboost.cbm'))
    return metrics, study, best_model

def train_neural_network(X_train, y_train, X_val, y_val, X_test, y_test):
    logging.info("--- Training Neural Network ---")
    input_dim = X_train.shape[1]
    
    def build_model():
        model = Sequential([
            Dense(256, activation='relu', input_shape=(input_dim,)),
            BatchNormalization(),
            Dropout(0.3),
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(1, activation='sigmoid') # Binary classification requires 1 output unit for sigmoid
        ])
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                      loss='binary_crossentropy',
                      metrics=['accuracy', tf.keras.metrics.Precision(), tf.keras.metrics.Recall(), tf.keras.metrics.AUC()])
        return model

    model = build_model()
    
    callbacks = [
        EarlyStopping(patience=10, restore_best_weights=True),
        ReduceLROnPlateau(factor=0.5, patience=5),
        CSVLogger(str(REPORTS_DIR / 'nn_training_log.csv')),
        ModelCheckpoint(str(MODELS_DIR / 'neural_network.keras'), save_best_only=True)
    ]
    
    # Sample for NN to prevent TensorFlow from hanging on Mac MPS Backend
    sample_size = min(10000, len(X_train))
    idx = np.random.choice(len(X_train), sample_size, replace=False)
    X_train_nn = X_train.iloc[idx]
    y_train_nn = y_train.iloc[idx]
    
    t0 = time.time()
    history = model.fit(X_train_nn, y_train_nn, epochs=20, batch_size=64, # Reduced epochs for testing
                        validation_data=(X_val, y_val), callbacks=callbacks, verbose=1)
    t_train = time.time() - t0
    
    t0 = time.time()
    probs = model.predict(X_test).ravel()
    preds = (probs > 0.5).astype(int)
    t_inf = time.time() - t0
    
    metrics = evaluate_model(y_test, preds, probs, 'Neural Network', t_train, t_inf, get_memory_usage())
    generate_visualizations(y_test, preds, probs, 'Neural Network')
    
    # Save .h5 as requested in addition to keras
    model.save(str(MODELS_DIR / 'neural_network.h5'))
    return metrics, None, model

def save_leaderboard(all_metrics):
    df_metrics = pd.DataFrame(all_metrics)
    
    # Rank models
    df_metrics['F1_Rank'] = df_metrics['F1 Score'].rank(ascending=False)
    df_metrics['Recall_Rank'] = df_metrics['Recall'].rank(ascending=False)
    df_metrics['Inf_Time_Rank'] = df_metrics['Inference Time (s)'].rank(ascending=True)
    
    df_metrics = df_metrics.sort_values(by=['F1_Rank', 'Recall_Rank', 'Inf_Time_Rank'])
    
    df_metrics.to_excel(REPORTS_DIR / 'training_results.xlsx', index=False)
    df_metrics.to_csv(REPORTS_DIR / 'leaderboard.csv', index=False)
    
    best_model_name = df_metrics.iloc[0]['Model']
    logging.info(f"Best Model Selected: {best_model_name}")
    return best_model_name

def main():
    X_train, y_train, X_val, y_val, X_test, y_test = load_processed_data()
    
    all_metrics = []
    
    models = [
        ('Random Forest', train_random_forest),
        ('XGBoost', train_xgboost),
        ('LightGBM', train_lightgbm),
        ('CatBoost', train_catboost)
    ]
    
    for name, train_func in models:
        metrics, study, model = train_func(X_train, y_train, X_val, y_val, X_test, y_test)
        all_metrics.append(metrics)
        clear_memory()
        
    best_model_name = save_leaderboard(all_metrics)
    
    # Copy best model to models/best_model/
    if best_model_name == 'Random Forest':
        shutil.copy(MODELS_DIR / 'random_forest.joblib', BEST_MODEL_DIR / 'model.joblib')
    elif best_model_name == 'XGBoost':
        shutil.copy(MODELS_DIR / 'xgboost.json', BEST_MODEL_DIR / 'model.json')
    elif best_model_name == 'LightGBM':
        shutil.copy(MODELS_DIR / 'lightgbm.txt', BEST_MODEL_DIR / 'model.txt')
    elif best_model_name == 'CatBoost':
        shutil.copy(MODELS_DIR / 'catboost.cbm', BEST_MODEL_DIR / 'model.cbm')
    elif best_model_name == 'Neural Network':
        shutil.copy(MODELS_DIR / 'neural_network.keras', BEST_MODEL_DIR / 'model.keras')

    # Note: Threat Analysis Agent needs the scaler and encoder, which should be copied here as well.
    logging.info("Phase 3 Pipeline Complete.")

if __name__ == "__main__":
    main()
