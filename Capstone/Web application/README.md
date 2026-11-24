# JobGuard AI: Intelligent Fake Job Posting Detection

An end-to-end Machine Learning web application designed to identify, analyze, and flag fraudulent recruitment listings and employment scams using **Logistic Regression** and **Support Vector Machine (LinearSVC)** with TF-IDF text vectorization, engineered metadata extraction, and calibrated confidence scoring.

---

## Key Highlights

- **Dual Machine Learning Engines**:
  - **Logistic Regression**: Class-weighted L2-penalized linear model delivering posterior probabilities of fraud.
  - **Support Vector Machine (LinearSVC)**: Maximum-margin hyperplane classifier calibrated with Platt's sigmoid scaling for robust probability estimates in high-dimensional sparse NLP spaces.
  - **Dual Consensus Ensemble**: Blended decision metric taking advantage of SVM margin separation and Logistic Regression calibration.
- **Engineered Feature Space (1,617 features)**:
  - Sublinear TF-IDF word and bigram text representations across Title, Company Profile, Description, Requirements, and Benefits.
  - Scaled tabular indicators: `has_company_logo`, `has_questions`, `telecommuting`, missing profile flags, text length, and high-risk scam triggers.
- **Explainable AI (XAI) & Red Flag Breakdown**:
  - Automatic detection and highlighting of scam keywords (Telegram/WhatsApp hiring, cashier check deposits, money mule indicators, crypto conversions).
  - Clear severity badges (`Critical`, `High`, `Medium`, `Low`) explaining *why* a listing was flagged.
  - Positive trust signals highlighting authentic corporate indicators.
- **Interactive Cyber-Defense Web Application**:
  - **Live Scanner**: Deep inspection of single job postings with real-time radial gauge animation.
  - **1-Click Preloaded Samples**: Instant testing of real tech/healthcare roles vs. notorious scam archetypes (Check Overpayment, Telegram Data Entry, Crypto Escrow).
  - **Model Comparison & Analytics**: Side-by-side performance cards, confusion matrices, and feature importance bars.
  - **Batch Job Scanner**: Multi-job scanning with tabular reporting and CSV upload.
  - **Scam Prevention Guide**: Practical threat intelligence on common recruitment scam archetypes.
  - **REST API**: Automated programmatic endpoints (`/api/predict`, `/api/batch-predict`, `/api/upload-csv`, `/api/metrics`).

---

## Model Architecture & Evaluation

Both models were trained and rigorously evaluated on a stratified 80/20 train/test split of 5,000 job postings (4,100 legitimate, 900 fraudulent):

| Metric | Logistic Regression | Support Vector Machine (LinearSVC) |
| :--- | :---: | :---: |
| **Accuracy** | **100.00%** | **100.00%** |
| **Precision** | **100.00%** | **100.00%** |
| **Recall** | **100.00%** | **100.00%** |
| **F1-Score** | **100.00%** | **100.00%** |
| **ROC-AUC** | **100.00%** | **100.00%** |
| **Inference Latency** | **< 15ms** | **< 15ms** |

### Confusion Matrix (Test Set: N = 1,000)
- **True Negatives (Legitimate classified as Legitimate)**: 820
- **False Positives (Legitimate flagged as Fake)**: 0
- **False Negatives (Fake missed as Legitimate)**: 0
- **True Positives (Fake identified as Fake)**: 180

---

## Project Directory Structure

```
Fake job posting detection/
├── app.py                      # FastAPI web application backend & REST endpoints
├── run_server.py               # Launcher script for FastAPI + Uvicorn server
├── start_website.bat           # 1-Click Windows batch launcher
├── README.md                   # Complete documentation
├── data/
│   └── fake_job_postings.csv   # EMSCAD-modeled dataset (5,000 postings)
├── models/
│   ├── logistic_regression_model.joblib  # Serialized Logistic Regression model
│   ├── svm_model.joblib                  # Serialized Calibrated LinearSVC model
│   ├── vectorizer.joblib                 # Fitted TF-IDF vectorizer (1,609 vocab)
│   ├── scaler.joblib                     # Fitted StandardScaler for metadata
│   └── metrics.json                      # Performance benchmark data & top features
├── src/
│   ├── __init__.py
│   ├── data_generator.py       # Realistic dataset synthesis
│   ├── preprocessor.py         # Text cleaning, regex normalizers, red flag analyzer
│   ├── train.py                # Model training, calibration, and evaluation pipeline
│   └── predictor.py            # Singleton inference engine & sample repository
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphism dark cyber-security design system
│   └── js/
│       └── app.js              # Client interactivity, gauge animation, API handler
└── templates/
    └── index.html              # Modern responsive single-page web dashboard
```

---

## Quick Start: Running the Website

### Method 1: 1-Click Launch (Windows)
Double-click `start_website.bat` in the project root folder.

### Method 2: Command Line
Open PowerShell or Command Prompt in this folder and run:

```bash
python run_server.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## REST API Documentation

### 1. Analyze Single Job Posting
- **Endpoint**: `POST /api/predict`
- **Payload**:
  ```json
  {
    "title": "URGENT: Work From Home Data Entry Assistant ($48/hr)",
    "company_profile": "",
    "description": "Urgent hiring! Contact HR on Telegram @hiring_manager to start today.",
    "requirements": "Must have checking account for check deposits.",
    "benefits": "Daily payouts via CashApp.",
    "telecommuting": 1,
    "has_company_logo": 0,
    "has_questions": 0,
    "model_choice": "both"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "data": {
      "is_fraudulent": true,
      "risk_score": 100.0,
      "risk_level": "Critical / High Risk Scam",
      "verdict": "HIGH ALERT: Fraudulent / Fake Job Posting Detected",
      "primary_model": "Dual Ensemble (LR + SVM)",
      "model_breakdown": {
        "logistic_regression": { "probability": 100.0, "is_fraudulent": true },
        "svm": { "probability": 100.0, "is_fraudulent": true }
      },
      "detected_keywords": ["telegram", "urgently hiring"],
      "red_flags": [
        {
          "severity": "Critical",
          "title": "Off-Platform Communication Request",
          "description": "Applicant is directed to interview or send details via Telegram or WhatsApp."
        }
      ]
    }
  }
  ```

### 2. Batch Predictions
- **Endpoint**: `POST /api/batch-predict`
- **Upload CSV**: `POST /api/upload-csv`
- **Model Evaluation Metrics**: `GET /api/metrics`
- **Instant Test Samples**: `GET /api/samples`
