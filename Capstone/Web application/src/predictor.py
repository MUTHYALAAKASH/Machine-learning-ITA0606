import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack

from src.preprocessor import (
    build_combined_text,
    extract_metadata_features,
    analyze_job_posting_red_flags
)

class FakeJobDetector:
    _instance = None

    def __init__(self, models_dir="models"):
        self.models_dir = models_dir
        self.lr_model = None
        self.svm_model = None
        self.vectorizer = None
        self.scaler = None
        self.metrics = None
        self._load_artifacts()

    @classmethod
    def get_instance(cls, models_dir="models"):
        if cls._instance is None:
            cls._instance = cls(models_dir)
        return cls._instance

    def _load_artifacts(self):
        lr_path = os.path.join(self.models_dir, "logistic_regression_model.joblib")
        svm_path = os.path.join(self.models_dir, "svm_model.joblib")
        vec_path = os.path.join(self.models_dir, "vectorizer.joblib")
        scaler_path = os.path.join(self.models_dir, "scaler.joblib")
        metrics_path = os.path.join(self.models_dir, "metrics.json")

        if os.path.exists(lr_path) and os.path.exists(svm_path):
            self.lr_model = joblib.load(lr_path)
            self.svm_model = joblib.load(svm_path)
            self.vectorizer = joblib.load(vec_path)
            self.scaler = joblib.load(scaler_path)
            
            if os.path.exists(metrics_path):
                with open(metrics_path, "r") as f:
                    self.metrics = json.load(f)
            print("FakeJobDetector: Models and artifacts loaded successfully.")
        else:
            print("FakeJobDetector: Models not yet found. Call train() or run train.py first.")

    def is_ready(self) -> bool:
        return (
            self.lr_model is not None and
            self.svm_model is not None and
            self.vectorizer is not None and
            self.scaler is not None
        )

    def predict_single(self, job_data: dict, model_choice: str = "both") -> dict:
        """
        Analyzes a single job posting.
        model_choice: 'logistic_regression', 'svm', or 'both'
        """
        if not self.is_ready():
            self._load_artifacts()
            if not self.is_ready():
                raise RuntimeError("Models are not trained or loaded yet.")

        # Convert to single-row dataframe
        df_row = pd.DataFrame([job_data])
        
        # 1. Clean & combine text
        combined_text = build_combined_text(df_row.iloc[0])
        
        # 2. Extract metadata
        meta_feats = extract_metadata_features(df_row)
        
        # 3. Transform features
        text_vec = self.vectorizer.transform([combined_text])
        meta_scaled = self.scaler.transform(meta_feats)
        X_input = hstack([text_vec, meta_scaled]).tocsr()

        # 4. Model Predictions
        lr_prob = float(self.lr_model.predict_proba(X_input)[0, 1])
        lr_pred = int(lr_prob >= 0.50)

        svm_prob = float(self.svm_model.predict_proba(X_input)[0, 1])
        svm_pred = int(svm_prob >= 0.50)

        # Consensus / Choice
        if model_choice == "logistic_regression":
            primary_score = lr_prob
            primary_pred = lr_pred
            primary_model_name = "Logistic Regression"
        elif model_choice == "svm":
            primary_score = svm_prob
            primary_pred = svm_pred
            primary_model_name = "Support Vector Machine"
        else: # Both / Ensemble
            primary_score = (lr_prob * 0.45 + svm_prob * 0.55) # slight weight to margin-maximizing SVM
            primary_pred = int(primary_score >= 0.50)
            primary_model_name = "Dual Ensemble (LR + SVM)"

        risk_percent = round(primary_score * 100, 2)
        
        if risk_percent < 25:
            risk_level = "Safe / Legitimate"
            badge_class = "safe"
            verdict = "Likely Legitimate Job Opportunity"
        elif risk_percent < 50:
            risk_level = "Low Risk"
            badge_class = "low"
            verdict = "Low Risk - Typical Legitimate Characteristics"
        elif risk_percent < 75:
            risk_level = "Suspicious / Moderate Risk"
            badge_class = "caution"
            verdict = "Warning: Several Scam Characteristics Detected"
        else:
            risk_level = "Critical / High Risk Scam"
            badge_class = "danger"
            verdict = "HIGH ALERT: Fraudulent / Fake Job Posting Detected"

        # Heuristic Red Flags & Explanations
        explanation = analyze_job_posting_red_flags(job_data)

        return {
            "is_fraudulent": bool(primary_pred == 1),
            "risk_score": risk_percent,
            "risk_level": risk_level,
            "badge_class": badge_class,
            "verdict": verdict,
            "primary_model": primary_model_name,
            "model_breakdown": {
                "logistic_regression": {
                    "name": "Logistic Regression",
                    "probability": round(lr_prob * 100, 2),
                    "is_fraudulent": bool(lr_pred == 1)
                },
                "svm": {
                    "name": "Support Vector Machine",
                    "probability": round(svm_prob * 100, 2),
                    "is_fraudulent": bool(svm_pred == 1)
                }
            },
            "detected_keywords": explanation["detected_keywords"],
            "red_flags": explanation["red_flags"],
            "trust_signals": explanation["trust_signals"]
        }

    def predict_batch(self, jobs_list: list[dict], model_choice: str = "both") -> list[dict]:
        """Runs predictions over a batch of job postings."""
        results = []
        for job in jobs_list:
            res = self.predict_single(job, model_choice)
            results.append({
                "title": job.get("title", "Untitled Job"),
                "company_profile": job.get("company_profile", "")[:80] + "..." if len(job.get("company_profile", "")) > 80 else job.get("company_profile", ""),
                "risk_score": res["risk_score"],
                "risk_level": res["risk_level"],
                "badge_class": res["badge_class"],
                "is_fraudulent": res["is_fraudulent"],
                "lr_prob": res["model_breakdown"]["logistic_regression"]["probability"],
                "svm_prob": res["model_breakdown"]["svm"]["probability"],
                "flag_count": len(res["red_flags"])
            })
        return results

    def get_sample_jobs(self) -> dict:
        """Returns curated legitimate and fraudulent job posting samples."""
        return {
            "legitimate": [
                {
                    "title": "Senior Backend Software Engineer (Python & Distributed Systems)",
                    "company_profile": "Nexus Cloud Technologies is a Series B enterprise cloud infrastructure company powering over 2,000 global corporate applications with 99.999% uptime.",
                    "description": "We are looking for an experienced Senior Backend Software Engineer to design, scale, and maintain our multi-tenant distributed streaming pipeline. You will collaborate with site reliability engineers, lead code reviews, architect gRPC microservices, and ensure adherence to strict security standards.",
                    "requirements": "5+ years of production experience in Python or Go. Strong foundation in distributed systems, PostgreSQL, Redis, and Kafka. Experience with Docker, Kubernetes, and AWS or GCP. Bachelor's or Master's degree in Computer Science or equivalent practical experience.",
                    "benefits": "Competitive salary ($145k-$180k) with meaningful equity. 100% company-covered medical, dental, and vision insurance. 401(k) with 4% matching. $2,500 annual continuing education budget. Flexible hybrid work schedule.",
                    "telecommuting": 1,
                    "has_company_logo": 1,
                    "has_questions": 1,
                    "employment_type": "Full-time"
                },
                {
                    "title": "Clinical Research Operations Coordinator",
                    "company_profile": "Meridian Health Solutions is an accredited clinical research hospital network dedicated to pioneering breakthrough oncology therapies and patient clinical trials.",
                    "description": "The Clinical Research Coordinator facilitates oncology trial execution, manages patient compliance records, coordinates IRB regulatory approvals, and liaises directly with clinical trial investigators and pharmaceutical sponsors.",
                    "requirements": "Bachelor's degree in Nursing, Life Sciences, or Public Health. Minimum 2 years of clinical research experience. ACRP or SOCRA certification preferred. Strict adherence to HIPAA guidelines and Good Clinical Practice (GCP).",
                    "benefits": "State pension retirement plan, full healthcare package, 25 days paid vacation, tuition assistance, and child daycare subsidy.",
                    "telecommuting": 0,
                    "has_company_logo": 1,
                    "has_questions": 1,
                    "employment_type": "Full-time"
                },
                {
                    "title": "Financial Planning & Analysis (FP&A) Analyst",
                    "company_profile": "Crestview Capital Advisory is an SEC-registered investment management enterprise overseeing $4.5B in institutional assets across North America.",
                    "description": "Join our corporate finance division as an FP&A Analyst. You will be responsible for preparing quarterly financial forecast models, variance analyses, board presentation decks, and evaluating capital allocation projects across business lines.",
                    "requirements": "Bachelor's in Finance, Accounting, or Economics. 2-4 years in corporate financial modeling or investment banking. Advanced Excel (VBA/macros) and PowerBI or Tableau proficiency. CFA Level 1 or CPA candidate preferred.",
                    "benefits": "Annual performance incentive bonus (15-25%), 401(k) matching, transit commuter benefits, subsidized gym membership, and comprehensive healthcare.",
                    "telecommuting": 0,
                    "has_company_logo": 1,
                    "has_questions": 1,
                    "employment_type": "Full-time"
                }
            ],
            "fraudulent": [
                {
                    "title": "URGENT: Work From Home Data Entry Assistant ($48/hr) - Immediate Start",
                    "company_profile": "",
                    "description": "URGENTLY HIRING! Are you looking for easy income from home? We are recruiting independent contractors for simple data typing and file forwarding. Work only 2-3 hours per day and make $1,200 to $2,500 every single week. No experience or resume needed! Flexible hours. All selected applicants receive an advance company check to purchase equipment (laptop, printer) from our certified vendor. Contact hiring manager Mr. David Wilson on Telegram right now: @DavidHR_Hiring or WhatsApp with your name and email to start today!",
                    "requirements": "Must have an active personal checking bank account to receive check deposits and wire transfers. Must be 18+ and have a smartphone with Telegram or WhatsApp.",
                    "benefits": "Daily payout via CashApp, Zelle, or Western Union. Free company laptop after 30 days. No interview required.",
                    "telecommuting": 1,
                    "has_company_logo": 0,
                    "has_questions": 0,
                    "employment_type": "Part-time"
                },
                {
                    "title": "Mystery Shopper & Quality Assurance Evaluator ($500/assignment)",
                    "company_profile": "International mystery customer audit agency evaluating major banking institutions.",
                    "description": "Earn easy cash in your spare time! We will mail you an official cashier's check for $3,800. Your assignment is to deposit the check at your local bank, keep $500 as your mystery evaluation fee, and test the transfer speed and customer service by wiring the remaining $3,300 via Western Union or Bitcoin ATM to our designated field supervisor. Report your findings back via email.",
                    "requirements": "Honest and dependable. Must have an active bank account open for at least 6 months. Ability to follow directions within 24 hours of check delivery.",
                    "benefits": "Immediate cash bonus, flexible timings, keep $500 per survey.",
                    "telecommuting": 1,
                    "has_company_logo": 0,
                    "has_questions": 0,
                    "employment_type": "Contract"
                },
                {
                    "title": "Remote Payment Processing Clerk / Crypto Escrow Agent",
                    "company_profile": "",
                    "description": "We are seeking a remote financial clearing assistant to assist with foreign currency transactions. Your primary responsibility is receiving corporate client payments into your personal account, converting funds to USDT / Bitcoin on cryptocurrency exchanges, and forwarding them to corporate wallets. High commission of 10% on every payment processed. Work from anywhere, anytime.",
                    "requirements": "Must have a bank account and verified crypto exchange account (Binance, Coinbase, or Kraken). Zero background check, instant start.",
                    "benefits": "10% daily commission, daily payouts, earn over $5,000 every week without prior training.",
                    "telecommuting": 1,
                    "has_company_logo": 0,
                    "has_questions": 0,
                    "employment_type": "Part-time"
                }
            ]
        }
