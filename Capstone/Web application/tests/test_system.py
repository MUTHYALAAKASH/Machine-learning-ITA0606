import os
import sys
import json
import unittest

# Ensure root path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.predictor import FakeJobDetector
from src.preprocessor import clean_text, count_suspicious_keywords, analyze_job_posting_red_flags

class TestFakeJobPostingDetection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.detector = FakeJobDetector.get_instance()
        cls.assertTrue(cls.detector.is_ready(), "Machine learning models and preprocessors must be loaded.")

    def test_text_cleaning(self):
        raw = "Check out https://scam-site.com/apply! Email us at hr@fakecorp.com or call +1 555-019-2834."
        cleaned = clean_text(raw)
        self.assertIn("url_link", cleaned)
        self.assertIn("email_address", cleaned)
        self.assertIn("phone_number", cleaned)

    def test_suspicious_keyword_counter(self):
        text = "Urgent hiring! Work from home data entry. Must have Telegram and cashier check."
        count, detected = count_suspicious_keywords(text)
        self.assertGreaterEqual(count, 3)
        self.assertIn("telegram", detected)
        self.assertIn("cashier check", detected)
        self.assertIn("work from home data entry", detected)

    def test_legitimate_job_prediction(self):
        samples = self.detector.get_sample_jobs()
        legit_job = samples["legitimate"][0]

        result = self.detector.predict_single(legit_job, model_choice="both")
        
        # Risk score should be low
        self.assertFalse(result["is_fraudulent"], "Legitimate job should not be classified as fraudulent.")
        self.assertLess(result["risk_score"], 35.0, "Risk score for legitimate job should be low.")
        self.assertIn("Safe", result["risk_level"])
        self.assertGreater(len(result["trust_signals"]), 0)

        # Check individual model breakdown
        lr = result["model_breakdown"]["logistic_regression"]
        svm = result["model_breakdown"]["svm"]
        self.assertFalse(lr["is_fraudulent"])
        self.assertFalse(svm["is_fraudulent"])
        self.assertLess(lr["probability"], 40.0)
        self.assertLess(svm["probability"], 40.0)

    def test_fraudulent_job_prediction(self):
        samples = self.detector.get_sample_jobs()
        scam_job = samples["fraudulent"][0]

        result = self.detector.predict_single(scam_job, model_choice="both")

        # Risk score should be high
        self.assertTrue(result["is_fraudulent"], "Scam job must be classified as fraudulent.")
        self.assertGreaterEqual(result["risk_score"], 80.0, "Risk score for scam job should be high.")
        self.assertEqual(result["badge_class"], "danger")
        self.assertGreater(len(result["red_flags"]), 0)
        self.assertGreater(len(result["detected_keywords"]), 0)

        # Check individual model breakdown
        lr = result["model_breakdown"]["logistic_regression"]
        svm = result["model_breakdown"]["svm"]
        self.assertTrue(lr["is_fraudulent"])
        self.assertTrue(svm["is_fraudulent"])
        self.assertGreaterEqual(lr["probability"], 80.0)
        self.assertGreaterEqual(svm["probability"], 80.0)

    def test_model_choice_modes(self):
        samples = self.detector.get_sample_jobs()
        scam = samples["fraudulent"][1]

        # Test LR only
        res_lr = self.detector.predict_single(scam, model_choice="logistic_regression")
        self.assertEqual(res_lr["primary_model"], "Logistic Regression")

        # Test SVM only
        res_svm = self.detector.predict_single(scam, model_choice="svm")
        self.assertEqual(res_svm["primary_model"], "Support Vector Machine")

        # Test Dual Consensus
        res_both = self.detector.predict_single(scam, model_choice="both")
        self.assertIn("Dual", res_both["primary_model"])

    def test_batch_prediction(self):
        samples = self.detector.get_sample_jobs()
        batch = samples["legitimate"] + samples["fraudulent"]

        results = self.detector.predict_batch(batch, model_choice="both")
        self.assertEqual(len(results), len(batch))

        # Check that legitimate jobs in batch are flagged safe and scams are flagged fake
        for i in range(len(samples["legitimate"])):
            self.assertFalse(results[i]["is_fraudulent"])
        for j in range(len(samples["fraudulent"])):
            idx = len(samples["legitimate"]) + j
            self.assertTrue(results[idx]["is_fraudulent"])

    def test_metrics_json_integrity(self):
        metrics_file = os.path.join("models", "metrics.json")
        self.assertTrue(os.path.exists(metrics_file), "metrics.json must exist.")
        
        with open(metrics_file, "r") as f:
            data = json.load(f)

        self.assertIn("logistic_regression", data)
        self.assertIn("svm", data)
        self.assertIn("dataset_stats", data)
        self.assertGreaterEqual(data["logistic_regression"]["accuracy"], 0.95)
        self.assertGreaterEqual(data["svm"]["accuracy"], 0.95)

if __name__ == "__main__":
    unittest.main()
