import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


APP_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = APP_DIR / "ml_models"

MODEL_PATH = MODEL_DIR / "triage_model.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


URGENCY_ORDER = {
    "Self-care": 1,
    "Routine": 2,
    "Soon": 3,
    "Urgent": 4,
    "Emergency": 5,
}


def load_metadata() -> dict[str, Any]:
    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Model metadata not found: {METADATA_PATH}"
        )

    with open(METADATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Triage model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def decode_json_list(value: str | None) -> list[str]:
    if not value:
        return []

    try:
        decoded_value = json.loads(value)

        if isinstance(decoded_value, list):
            return [str(item) for item in decoded_value]

    except json.JSONDecodeError:
        return []

    return []


def build_feature_row(referral) -> pd.DataFrame:
    metadata = load_metadata()

    symptoms = decode_json_list(
        referral.extracted_symptoms
    )

    conditions = decode_json_list(
        referral.extracted_conditions
    )

    symptom_set = set(symptoms)
    condition_set = set(conditions)

    red_flag_value = 1 if referral.red_flag_detected else 0

    estimated_pain_score = 8 if referral.red_flag_detected else 3

    row = {
        "age": referral.patient.age,
        "duration_days": referral.duration_days or 0,
        "pain_score": estimated_pain_score,
        "diabetes": int("diabetes" in condition_set),
        "heart_disease": int("heart disease" in condition_set),
        "asthma": int("asthma" in condition_set),
        "bp_high": int("hypertension" in condition_set),
        "pregnancy": int("pregnancy" in condition_set),
        "previous_admissions": 0,
        "waiting_days": referral.waiting_days,
        "previous_missed_appointments": 0,
        "red_flag": red_flag_value,
        "gender": referral.patient.gender,
        "department": referral.department,
    }

    for symptom_feature in metadata["symptom_features"]:
        symptom_name = (
            symptom_feature
            .replace("symptom_", "")
            .replace("_", " ")
        )

        row[symptom_feature] = int(
            symptom_name in symptom_set
        )

    feature_columns = (
        metadata["numeric_features"]
        + metadata["categorical_features"]
        + metadata["symptom_features"]
    )

    return pd.DataFrame([row])[feature_columns]


def calculate_risk_score(
    class_labels,
    probabilities,
) -> float:
    weighted_score = 0.0
    max_score = max(URGENCY_ORDER.values())

    for label, probability in zip(
        class_labels,
        probabilities,
    ):
        weighted_score += (
            URGENCY_ORDER.get(label, 1)
            / max_score
            * probability
        )

    return round(float(weighted_score), 4)


def apply_safety_override(
    predicted_urgency: str,
    red_flag_detected: bool,
) -> str:
    if not red_flag_detected:
        return predicted_urgency

    if URGENCY_ORDER[predicted_urgency] < URGENCY_ORDER["Urgent"]:
        return "Urgent"

    return predicted_urgency


def generate_explanation(
    referral,
    predicted_urgency: str,
    final_urgency: str,
    confidence: float,
    risk_score: float,
) -> str:
    symptoms = decode_json_list(
        referral.extracted_symptoms
    )

    conditions = decode_json_list(
        referral.extracted_conditions
    )

    symptom_text = (
        ", ".join(symptoms)
        if symptoms
        else "no known symptoms extracted"
    )

    condition_text = (
        ", ".join(conditions)
        if conditions
        else "no known existing conditions extracted"
    )

    explanation = (
        f"The triage model predicted {predicted_urgency} "
        f"with {round(confidence * 100)}% confidence. "
        f"Extracted symptoms include {symptom_text}. "
        f"Existing conditions include {condition_text}. "
        f"The calculated triage risk score is "
        f"{round(risk_score * 100)}%."
    )

    if referral.red_flag_detected:
        explanation += (
            f" A red-flag rule was detected: "
            f"{referral.red_flag_reason}"
        )

    if final_urgency != predicted_urgency:
        explanation += (
            f" The final urgency was increased to "
            f"{final_urgency} because of the safety "
            f"red-flag override."
        )

    explanation += (
        " This is a decision-support result and "
        "requires clinician review."
    )

    return explanation


def predict_triage(referral) -> dict[str, Any]:
    model = load_model()
    metadata = load_metadata()

    feature_row = build_feature_row(referral)

    predicted_urgency = model.predict(feature_row)[0]

    probabilities = model.predict_proba(feature_row)[0]
    class_labels = model.classes_

    confidence = round(float(max(probabilities)), 4)

    risk_score = calculate_risk_score(
        class_labels=class_labels,
        probabilities=probabilities,
    )

    final_urgency = apply_safety_override(
        predicted_urgency=predicted_urgency,
        red_flag_detected=referral.red_flag_detected,
    )

    explanation = generate_explanation(
        referral=referral,
        predicted_urgency=predicted_urgency,
        final_urgency=final_urgency,
        confidence=confidence,
        risk_score=risk_score,
    )

    return {
        "predicted_urgency": predicted_urgency,
        "final_urgency": final_urgency,
        "risk_score": risk_score,
        "confidence": confidence,
        "human_review_required": True,
        "explanation": explanation,
        "model_name": metadata["model_name"],
    }