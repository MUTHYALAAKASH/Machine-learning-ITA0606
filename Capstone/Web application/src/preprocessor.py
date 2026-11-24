import re
import string
import numpy as np
import pandas as pd

# Curated list of high-risk scam triggers commonly seen in fraudulent job postings
SUSPICIOUS_KEYWORDS = [
    "telegram", "whatsapp", "wire transfer", "western union", "moneygram",
    "cashier check", "cashiers check", "deposit check", "personal account",
    "crypto", "bitcoin", "usdt", "gift card", "zelle", "cashapp", "venmo",
    "no experience required", "no interview", "start immediately",
    "daily payout", "weekly payout", "package reshipment", "mystery shopper",
    "secret shopper", "dr.", "kindly", "urgently hiring", "guaranteed income",
    "easy money", "work from home data entry", "typing job", "advance fee"
]

def clean_text(text: str) -> str:
    """Cleans and standardizes raw text."""
    if not isinstance(text, str):
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Replace URLs
    text = re.sub(r'https?://\S+|www\.\S+', ' url_link ', text)
    
    # Replace Email addresses
    text = re.sub(r'\S+@\S+', ' email_address ', text)
    
    # Replace phone numbers
    text = re.sub(r'\+?\d[\d -]{8,}\d', ' phone_number ', text)
    
    # Remove special punctuation but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def build_combined_text(row) -> str:
    """Combines all textual fields of a job posting into a unified corpus."""
    fields = [
        str(row.get("title", "") or ""),
        str(row.get("company_profile", "") or ""),
        str(row.get("description", "") or ""),
        str(row.get("requirements", "") or ""),
        str(row.get("benefits", "") or "")
    ]
    raw_combined = " ".join(fields)
    return clean_text(raw_combined)

def count_suspicious_keywords(text: str) -> tuple[int, list[str]]:
    """Counts matching suspicious phrases and returns detected keywords."""
    text_lower = text.lower()
    detected = []
    count = 0
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in text_lower:
            count += 1
            detected.append(kw)
    return count, detected

def extract_metadata_features(df: pd.DataFrame) -> np.ndarray:
    """
    Extracts tabular metadata features:
    1. has_company_logo (0/1)
    2. has_questions (0/1)
    3. telecommuting (0/1)
    4. missing_company_profile (0/1)
    5. missing_requirements (0/1)
    6. missing_benefits (0/1)
    7. text_char_length (numeric)
    8. suspicious_keyword_count (numeric)
    """
    feats = []
    for _, row in df.iterrows():
        logo = int(row.get("has_company_logo", 0) or 0)
        questions = int(row.get("has_questions", 0) or 0)
        telecom = int(row.get("telecommuting", 0) or 0)
        
        prof = str(row.get("company_profile", "") or "").strip()
        reqs = str(row.get("requirements", "") or "").strip()
        bens = str(row.get("benefits", "") or "").strip()
        
        miss_prof = 1 if len(prof) < 10 else 0
        miss_reqs = 1 if len(reqs) < 10 else 0
        miss_bens = 1 if len(bens) < 10 else 0
        
        combined_text = build_combined_text(row)
        char_len = len(combined_text)
        kw_count, _ = count_suspicious_keywords(combined_text)
        
        feats.append([
            logo,
            questions,
            telecom,
            miss_prof,
            miss_reqs,
            miss_bens,
            char_len,
            kw_count
        ])
        
    return np.array(feats, dtype=float)

def analyze_job_posting_red_flags(job_dict: dict) -> dict:
    """
    Heuristic rule-based analyzer providing transparent explanations and red flags.
    """
    red_flags = []
    trust_signals = []
    
    title = str(job_dict.get("title", "") or "").strip()
    profile = str(job_dict.get("company_profile", "") or "").strip()
    desc = str(job_dict.get("description", "") or "").strip()
    reqs = str(job_dict.get("requirements", "") or "").strip()
    has_logo = int(job_dict.get("has_company_logo", 0) or 0)
    has_questions = int(job_dict.get("has_questions", 0) or 0)
    
    full_text = f"{title} {profile} {desc} {reqs}"
    kw_count, detected_kws = count_suspicious_keywords(full_text)
    
    # Red Flag checks
    if has_logo == 0:
        red_flags.append({
            "severity": "Medium",
            "title": "Missing Company Branding / Logo",
            "description": "Legitimate employers typically maintain an official profile with corporate logo branding."
        })
    else:
        trust_signals.append("Official company logo/branding provided.")
        
    if has_questions == 0:
        red_flags.append({
            "severity": "Low",
            "title": "No Screening Questions",
            "description": "Scammers rarely configure structured application screening questionnaires."
        })
    else:
        trust_signals.append("Structured applicant screening questions configured.")
        
    if len(profile) < 20:
        red_flags.append({
            "severity": "High",
            "title": "Missing or Vague Company Profile",
            "description": "The posting contains no verifiable company background, corporate history, or identity."
        })
    else:
        trust_signals.append("Comprehensive company background information provided.")
        
    # Check for direct chat app recruitment
    if any(app in full_text.lower() for app in ["telegram", "whatsapp"]):
        red_flags.append({
            "severity": "Critical",
            "title": "Off-Platform Communication Request",
            "description": "Applicant is directed to interview or send details via Telegram or WhatsApp, a hallmark of recruitment scams."
        })
        
    # Check for financial/banking transaction triggers
    if any(term in full_text.lower() for term in ["cashier check", "wire transfer", "western union", "zelle", "deposit check", "personal account", "bitcoin"]):
        red_flags.append({
            "severity": "Critical",
            "title": "Financial Transaction / Check Cashing Request",
            "description": "Mentions checks, wire transfers, crypto wallets, or using personal bank accounts for company purchases."
        })
        
    # Check for unrealistic promises
    if any(term in full_text.lower() for term in ["no experience required", "easy money", "no interview", "guaranteed income"]):
        red_flags.append({
            "severity": "High",
            "title": "Unrealistic Hiring Guarantees",
            "description": "Promises high pay with zero prior experience, immediate hiring without technical interview."
        })
        
    return {
        "detected_keywords": detected_kws,
        "red_flags": red_flags,
        "trust_signals": trust_signals
    }
