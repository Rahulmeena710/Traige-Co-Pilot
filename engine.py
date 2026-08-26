import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from transformers import pipeline

class TriageEngine:
    def __init__(self):
        # Load Hugging Face zero-shot classification pipeline for symptom extraction
        self.nlp_pipeline = pipeline(
            "zero-shot-classification", 
            model="facebook/bart-large-mnli"
        )
        self.candidate_symptoms = [
            "chest pain", "shortness of breath", "fever", 
            "dizziness", "abdominal pain", "headache", "trauma"
        ]
        
        # Train age-aware risk classifier on baseline training data
        self.model = self._train_baseline_model()

    def _train_baseline_model(self):
        # Synthetic baseline dataset: age, heart_rate, sbp, spo2, temp, severity_score
        np.random.seed(42)
        X_train = np.random.rand(200, 5) * [80, 80, 80, 15, 4] + [5, 50, 80, 85, 36]
        # Escalation-biased labels (1 = High Risk, 0 = Low Risk)
        y_train = (
            (X_train[:, 0] > 65) | (X_train[:, 0] < 5) | # Pediatric / Geriatric boost
            (X_train[:, 1] > 110) | (X_train[:, 3] < 92)
        ).astype(int)

        rf = RandomForestClassifier(n_estimators=50, random_state=42)
        rf.fit(X_train, y_train)
        return rf

    def extract_nlp_symptoms(self, text):
        if not text:
            return []
        res = self.nlp_pipeline(text, candidate_labels=self.candidate_symptoms)
        # Extract symptoms with confidence score > 0.4
        extracted = [
            label for label, score in zip(res["labels"], res["scores"]) if score > 0.4
        ]
        return extracted

    def evaluate_patient(self, patient):
        """
        Calculates age-aware risk, uncertainty, and escalation-biased scores.
        """
        vitals = np.array([[
            patient['age'], patient['hr'], patient['sbp'], 
            patient['spo2'], patient['temp']
        ]])
        
        # Base ML probability & uncertainty (entropy-based)
        probs = self.model.predict_proba(vitals)[0]
        p_high_risk = probs[1] if len(probs) > 1 else probs[0]
        uncertainty = -np.sum(probs * np.log2(probs + 1e-9))  # Shannon entropy

        # Escalation-biased adjustments
        risk_score = p_high_risk * 100

        # Age-aware multipliers (Pediatric < 5 or Geriatric > 65)
        if patient['age'] < 5 or patient['age'] > 65:
            risk_score *= 1.25

        # Critical symptom & vital signs hard escalation flags
        critical_symptoms = ["chest pain", "shortness of breath"]
        has_critical_symptom = any(s in patient['symptoms'] for s in critical_symptoms)
        if has_critical_symptom or patient['spo2'] < 90 or patient['hr'] > 120:
            risk_score += 20.0

        # High uncertainty escalation boost
        if uncertainty > 0.8:
            risk_score += 10.0

        final_score = float(np.clip(risk_score, 0, 100))
        
        # Categorize Triage Level
        if final_score >= 70:
            category = "P1 - Critical"
        elif final_score >= 40:
            category = "P2 - Urgent"
        else:
            category = "P3 - Non-Urgent"

        return round(final_score, 1), round(uncertainty, 2), category