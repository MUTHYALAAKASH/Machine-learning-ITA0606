import os
import sys
import json
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

from src.data_generator import generate_job_dataset
from src.preprocessor import (
    build_combined_text,
    extract_metadata_features
)

def train_and_evaluate_models():
    print("=" * 65)
    print("  INTELLIGENT FAKE JOB DETECTION: MODEL TRAINING PIPELINE")
    print("  Logistic Regression vs. Support Vector Machine (SVM)")
    print("=" * 65)
    
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    data_path = os.path.join("data", "fake_job_postings.csv")
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Generating realistic dataset...")
        df = generate_job_dataset(num_samples=5000, scam_ratio=0.18)
        df.to_csv(data_path, index=False)
    else:
        print(f"Loading existing dataset from {data_path}...")
        df = pd.read_csv(data_path)
        
    print(f"Total postings: {len(df)}")
    fraud_count = df['fraudulent'].sum()
    legit_count = len(df) - fraud_count
    print(f"Class distribution: {legit_count} Legitimate ({legit_count/len(df)*100:.1f}%), {fraud_count} Fraudulent ({fraud_count/len(df)*100:.1f}%)")
    
    # Preprocessing text and metadata
    print("\n[Step 1/5] Preprocessing text and extracting metadata features...")
    df['combined_text'] = df.apply(build_combined_text, axis=1)
    meta_features = extract_metadata_features(df)
    
    # Ensure standard numpy arrays (compatible with pandas 3.0+ pyarrow strings)
    text_array = np.array(df['combined_text'].tolist(), dtype=object)
    y = np.array(df['fraudulent'].tolist(), dtype=int)
    
    # Train/Test Split (80/20 Stratified)
    print("\n[Step 2/5] Performing stratified 80/20 train/test split...")
    (
        text_train, text_test,
        meta_train, meta_test,
        y_train, y_test
    ) = train_test_split(
        text_array,
        meta_features,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print(f"Training samples: {len(y_train)} (Fraud: {y_train.sum()})")
    print(f"Testing samples:  {len(y_test)} (Fraud: {y_test.sum()})")
    
    # Feature Vectorization on Train Only
    print("\n[Step 3/5] Vectorizing text with TF-IDF and scaling metadata...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        stop_words='english'
    )
    X_train_text = vectorizer.fit_transform(text_train)
    X_test_text = vectorizer.transform(text_test)
    
    scaler = StandardScaler()
    X_train_meta = scaler.fit_transform(meta_train)
    X_test_meta = scaler.transform(meta_test)
    
    X_train = hstack([X_train_text, X_train_meta]).tocsr()
    X_test = hstack([X_test_text, X_test_meta]).tocsr()
    
    print(f"Total feature space dimension: {X_train.shape[1]} features")
    
    # Model 1: Logistic Regression
    print("\n[Step 4/5] Training Model 1: Logistic Regression (balanced class weights)...")
    t0 = time.time()
    lr_model = LogisticRegression(
        class_weight='balanced',
        C=1.5,
        max_iter=1000,
        random_state=42
    )
    lr_model.fit(X_train, y_train)
    lr_train_time = time.time() - t0
    print(f"Logistic Regression trained in {lr_train_time:.2f} seconds.")
    
    # Model 2: Support Vector Machine (LinearSVC with Probability Calibration)
    print("\nTraining Model 2: Support Vector Machine (LinearSVC + CalibratedClassifierCV)...")
    t0 = time.time()
    base_svc = LinearSVC(
        class_weight='balanced',
        C=1.0,
        random_state=42,
        max_iter=2000
    )
    svm_model = CalibratedClassifierCV(
        estimator=base_svc,
        method='sigmoid',
        cv=3
    )
    svm_model.fit(X_train, y_train)
    svm_train_time = time.time() - t0
    print(f"Support Vector Machine trained in {svm_train_time:.2f} seconds.")
    
    # Base SVC fit for feature weights interpretation
    base_svc.fit(X_train, y_train)
    
    # Evaluation
    print("\n[Step 5/5] Evaluating performance on test set...")
    
    # LR Predictions
    lr_pred = lr_model.predict(X_test)
    lr_prob = lr_model.predict_proba(X_test)[:, 1]
    lr_acc = accuracy_score(y_test, lr_pred)
    lr_prec = precision_score(y_test, lr_pred)
    lr_rec = recall_score(y_test, lr_pred)
    lr_f1 = f1_score(y_test, lr_pred)
    lr_auc = roc_auc_score(y_test, lr_prob)
    lr_cm = confusion_matrix(y_test, lr_pred).tolist()
    
    # SVM Predictions
    svm_pred = svm_model.predict(X_test)
    svm_prob = svm_model.predict_proba(X_test)[:, 1]
    svm_acc = accuracy_score(y_test, svm_pred)
    svm_prec = precision_score(y_test, svm_pred)
    svm_rec = recall_score(y_test, svm_pred)
    svm_f1 = f1_score(y_test, svm_pred)
    svm_auc = roc_auc_score(y_test, svm_prob)
    svm_cm = confusion_matrix(y_test, svm_pred).tolist()
    
    print("\n" + "=" * 65)
    print("                  MODEL COMPARISON SUMMARY")
    print("=" * 65)
    print(f"{'Metric':<20} | {'Logistic Regression':<20} | {'Support Vector Machine':<20}")
    print("-" * 65)
    print(f"{'Accuracy':<20} | {lr_acc*100:>18.2f}% | {svm_acc*100:>18.2f}%")
    print(f"{'Precision':<20} | {lr_prec*100:>18.2f}% | {svm_prec*100:>18.2f}%")
    print(f"{'Recall':<20} | {lr_rec*100:>18.2f}% | {svm_rec*100:>18.2f}%")
    print(f"{'F1-Score':<20} | {lr_f1*100:>18.2f}% | {svm_f1*100:>18.2f}%")
    print(f"{'ROC-AUC':<20} | {lr_auc*100:>18.2f}% | {svm_auc*100:>18.2f}%")
    print("=" * 65)
    
    # Extract Feature Importance (Top Words)
    feature_names = vectorizer.get_feature_names_out().tolist()
    metadata_names = [
        "has_logo", "has_questions", "telecommuting",
        "missing_profile", "missing_reqs", "missing_bens",
        "char_len", "suspicious_kw_count"
    ]
    all_feature_names = feature_names + metadata_names
    
    # LR top coefficients
    lr_coefs = lr_model.coef_[0]
    top_fraud_idx_lr = np.argsort(lr_coefs)[-15:][::-1]
    top_legit_idx_lr = np.argsort(lr_coefs)[:15]
    
    top_fraud_words_lr = [{"feature": all_feature_names[i], "weight": float(lr_coefs[i])} for i in top_fraud_idx_lr]
    top_legit_words_lr = [{"feature": all_feature_names[i], "weight": float(lr_coefs[i])} for i in top_legit_idx_lr]
    
    # Base SVC top coefficients
    svc_coefs = base_svc.coef_[0]
    top_fraud_idx_svc = np.argsort(svc_coefs)[-15:][::-1]
    top_legit_idx_svc = np.argsort(svc_coefs)[:15]
    
    top_fraud_words_svc = [{"feature": all_feature_names[i], "weight": float(svc_coefs[i])} for i in top_fraud_idx_svc]
    top_legit_words_svc = [{"feature": all_feature_names[i], "weight": float(svc_coefs[i])} for i in top_legit_idx_svc]
    
    # Save artifacts
    print("\nSaving trained models and vectorizer...")
    joblib.dump(lr_model, os.path.join("models", "logistic_regression_model.joblib"))
    joblib.dump(svm_model, os.path.join("models", "svm_model.joblib"))
    joblib.dump(vectorizer, os.path.join("models", "vectorizer.joblib"))
    joblib.dump(scaler, os.path.join("models", "scaler.joblib"))
    
    metrics = {
        "dataset_stats": {
            "total_samples": len(df),
            "legitimate_samples": int(legit_count),
            "fraudulent_samples": int(fraud_count),
            "fraud_ratio": float(fraud_count / len(df)),
            "train_size": len(y_train),
            "test_size": len(y_test)
        },
        "logistic_regression": {
            "name": "Logistic Regression",
            "accuracy": float(lr_acc),
            "precision": float(lr_prec),
            "recall": float(lr_rec),
            "f1_score": float(lr_f1),
            "roc_auc": float(lr_auc),
            "confusion_matrix": lr_cm,
            "training_time_sec": float(lr_train_time),
            "top_fraud_features": top_fraud_words_lr,
            "top_legit_features": top_legit_words_lr
        },
        "svm": {
            "name": "Support Vector Machine (LinearSVC)",
            "accuracy": float(svm_acc),
            "precision": float(svm_prec),
            "recall": float(svm_rec),
            "f1_score": float(svm_f1),
            "roc_auc": float(svm_auc),
            "confusion_matrix": svm_cm,
            "training_time_sec": float(svm_train_time),
            "top_fraud_features": top_fraud_words_svc,
            "top_legit_features": top_legit_words_svc
        }
    }
    
    with open(os.path.join("models", "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("Training artifacts successfully saved in `models/` directory.")
    return metrics

if __name__ == "__main__":
    train_and_evaluate_models()
