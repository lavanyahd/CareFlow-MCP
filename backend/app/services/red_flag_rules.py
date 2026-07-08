from typing import Any


def evaluate_red_flags(
    age: int,
    symptoms: list[str],
    conditions: list[str],
) -> dict[str, Any]:
    symptom_set = set(symptoms)
    condition_set = set(conditions)

    detected_reasons: list[str] = []
    highest_score = 0.0

    if {
        "chest pain",
        "shortness of breath",
    }.issubset(symptom_set):
        detected_reasons.append(
            "Chest pain with shortness of breath detected."
        )
        highest_score = max(highest_score, 0.95)

    if (
        "chest pain" in symptom_set
        and "heart disease" in condition_set
    ):
        detected_reasons.append(
            "Chest pain with a history of heart disease detected."
        )
        highest_score = max(highest_score, 0.95)

    if (
        "chest pain" in symptom_set
        and "diabetes" in condition_set
    ):
        detected_reasons.append(
            "Chest pain with diabetes detected."
        )
        highest_score = max(highest_score, 0.85)

    if (
        age >= 50
        and {
            "blood in stool",
            "weight loss",
        }.issubset(symptom_set)
    ):
        detected_reasons.append(
            "Blood in stool and unexplained weight loss "
            "detected in a patient aged 50 or older."
        )
        highest_score = max(highest_score, 0.90)

    neurological_symptoms = {
        "weakness",
        "speech difficulty",
    }

    if (
        "severe headache" in symptom_set
        and symptom_set.intersection(
            neurological_symptoms
        )
    ):
        detected_reasons.append(
            "Severe headache with neurological symptoms detected."
        )
        highest_score = max(highest_score, 1.0)

    if (
        "pregnancy" in condition_set
        and "severe abdominal pain" in symptom_set
    ):
        detected_reasons.append(
            "Pregnancy with severe abdominal pain detected."
        )
        highest_score = max(highest_score, 0.95)

    red_flag_detected = len(detected_reasons) > 0

    if red_flag_detected:
        reason = " ".join(detected_reasons)
    else:
        reason = "No configured red-flag combinations detected."

    return {
        "red_flag_detected": red_flag_detected,
        "red_flag_score": highest_score,
        "red_flag_reason": reason,
    }