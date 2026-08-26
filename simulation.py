import pandas as pd
import random

def generate_patient_records(count=22):
    symptom_pool = [
        "Chest tightness and severe sweating", 
        "Fever and persistent cough", 
        "Mild headache and runny nose", 
        "Sudden dizziness with numbness", 
        "Severe abdominal pain", 
        "Pediatric lethargy with high fever",
        "Minor skin rash"
    ]

    patients = []
    for i in range(1, count + 1):
        # Generate mixed demographics (Pediatric, Adult, Geriatric)
        age_group = random.choices(["pediatric", "adult", "geriatric"], weights=[0.2, 0.5, 0.3])[0]
        if age_group == "pediatric":
            age = random.randint(1, 12)
        elif age_group == "geriatric":
            age = random.randint(66, 88)
        else:
            age = random.randint(18, 64)

        patient = {
            "patient_id": f"P-{100+i}",
            "age": age,
            "hr": random.randint(55, 135),
            "sbp": random.randint(85, 160),
            "spo2": random.randint(88, 100),
            "temp": round(random.uniform(36.0, 39.5), 1),
            "clinical_notes": random.choice(symptom_pool),
            "surge_level": "1x Normal"
        }
        patients.append(patient)
    return patients

def apply_surge_condition(patient_list, multiplier=3):
    """
    Simulates a 3x surge event by accelerating critical queue shifts.
    """
    surged_list = []
    for p in patient_list:
        p_copy = p.copy()
        p_copy["surge_level"] = f"{multiplier}x Surge"
        # Surge conditions aggravate vital strain in high-risk patients
        if p_copy["hr"] > 100 or p_copy["spo2"] < 92:
            p_copy["hr"] += random.randint(5, 15)
            p_copy["spo2"] = max(80, p_copy["spo2"] - random.randint(1, 4))
        surged_list.append(p_copy)
    return surged_list