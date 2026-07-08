import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


APP_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = APP_DIR / "ml_models"

MODEL_PATH = MODEL_DIR / "dna_model.pkl"
METADATA_PATH = MODEL_DIR / "dna_model_metadata.json"


DNA_RISK_ORDER = {
    "Low": 0.25,
    "Medium": 0.65,
    "High": 1.0,
}


def load_metadata() -> dict[str, Any]:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"DNA model metadata not found: {METADATA_PATH}"
        )

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"DNA model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def build_feature_row(referral) -> pd.DataFrame:
    metadata = load_metadata()

    row = {
        "age": referral.patient.age,
        "waiting_days": referral.waiting_days,
        "previous_missed_appointments": 0,
        "previous_cancellations": 0,
        "reminder_sent": 1,
        "department": referral.department,
        "appointment_day": "Monday",
        "appointment_time": "Morning",
        "distance_band": "5-10 km",
    }

    feature_columns = (
        metadata["numeric_features"]
        + metadata["categorical_features"]
    )

    return pd.DataFrame([row])[feature_columns]


def calculate_dna_risk_score(
    class_labels,
    probabilities,
) -> float:
    risk_score = 0.0

    for label, probability in zip(
        class_labels,
        probabilities,
    ):
        risk_score += DNA_RISK_ORDER.get(label, 0.25) * probability

    return round(float(risk_score), 4)


def get_recommended_action(
    dna_risk: str,
    risk_score: float,
) -> str:
    if dna_risk == "High" or risk_score >= 0.75:
        return (
            "High DNA risk. Send SMS reminder, make phone confirmation, "
            "and consider flexible appointment options."
        )

    if dna_risk == "Medium" or risk_score >= 0.45:
        return (
            "Medium DNA risk. Send reminder and confirm appointment "
            "closer to the appointment date."
        )

    return (
        "Low DNA risk. Standard reminder is sufficient."
    )


def predict_dna(referral) -> dict[str, Any]:
    model = load_model()
    metadata = load_metadata()

    feature_row = build_feature_row(referral)

    dna_risk = model.predict(feature_row)[0]

    probabilities = model.predict_proba(feature_row)[0]
    class_labels = model.classes_

    confidence = round(float(max(probabilities)), 4)

    risk_score = calculate_dna_risk_score(
        class_labels=class_labels,
        probabilities=probabilities,
    )

    recommended_action = get_recommended_action(
        dna_risk=dna_risk,
        risk_score=risk_score,
    )

    return {
        "dna_risk": dna_risk,
        "risk_score": risk_score,
        "confidence": confidence,
        "appointment_day": "Monday",
        "appointment_time": "Morning",
        "distance_band": "5-10 km",
        "previous_missed_appointments": 0,
        "previous_cancellations": 0,
        "reminder_sent": True,
        "recommended_action": recommended_action,
        "model_name": metadata["model_name"],
    }