import json


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


def build_referral_context(
    referral,
    latest_triage,
    latest_dna,
    latest_review,
) -> dict:
    symptoms = decode_json_list(referral.extracted_symptoms)
    conditions = decode_json_list(referral.extracted_conditions)

    return {
        "patient_id": referral.patient.patient_id,
        "age": referral.patient.age,
        "gender": referral.patient.gender,
        "department": referral.department,
        "waiting_days": referral.waiting_days,
        "status": referral.status,
        "referral_text": referral.referral_text,
        "symptoms": symptoms,
        "conditions": conditions,
        "duration_days": referral.duration_days,
        "red_flag_detected": referral.red_flag_detected,
        "red_flag_score": referral.red_flag_score,
        "red_flag_reason": referral.red_flag_reason,
        "triage": latest_triage,
        "dna": latest_dna,
        "review": latest_review,
    }


def create_summary_answer(context: dict) -> str:
    symptoms = (
        ", ".join(context["symptoms"])
        if context["symptoms"]
        else "no symptoms extracted"
    )

    conditions = (
        ", ".join(context["conditions"])
        if context["conditions"]
        else "no existing conditions extracted"
    )

    answer = (
        f"Patient {context['patient_id']} is a "
        f"{context['age']}-year-old {context['gender']} patient referred to "
        f"{context['department']}. The referral note mentions: "
        f"{context['referral_text']} Extracted symptoms are {symptoms}. "
        f"Extracted conditions are {conditions}. "
    )

    if context["red_flag_detected"]:
        answer += (
            f"A red flag was detected with score "
            f"{round(context['red_flag_score'] * 100)}%. "
            f"Reason: {context['red_flag_reason']} "
        )
    else:
        answer += "No configured red-flag combination was detected. "

    if context["triage"] is not None:
        answer += (
            f"The latest triage prediction is "
            f"{context['triage'].final_urgency} with "
            f"{round(context['triage'].confidence * 100)}% confidence. "
        )

    if context["dna"] is not None:
        answer += (
            f"The latest DNA missed appointment risk is "
            f"{context['dna'].dna_risk}. Recommended action: "
            f"{context['dna'].recommended_action} "
        )

    if context["review"] is not None:
        answer += (
            f"The latest clinician review decision is "
            f"{context['review'].decision}, with final urgency "
            f"{context['review'].final_urgency}. "
        )

    return answer


def answer_question(question: str, context: dict) -> dict:
    question_lower = question.lower()
    sources = []

    if (
        "summary" in question_lower
        or "summarize" in question_lower
        or "overview" in question_lower
    ):
        sources = [
            "Referral note",
            "Extracted symptoms",
            "Red-flag assessment",
            "Triage result",
            "DNA result",
            "Clinician review",
        ]

        answer = create_summary_answer(context)

    elif "red flag" in question_lower or "red-flag" in question_lower:
        sources = [
            "Red-flag assessment",
            "Extracted symptoms",
            "Referral note",
        ]

        if context["red_flag_detected"]:
            answer = (
                f"Yes, a red flag was detected for patient "
                f"{context['patient_id']}. The red-flag score is "
                f"{round(context['red_flag_score'] * 100)}%. "
                f"The reason is: {context['red_flag_reason']}"
            )
        else:
            answer = (
                f"No configured red-flag combination was detected for "
                f"patient {context['patient_id']}."
            )

    elif (
        "triage" in question_lower
        or "urgency" in question_lower
        or "emergency" in question_lower
        or "urgent" in question_lower
    ):
        sources = [
            "Triage result",
            "Red-flag assessment",
            "Referral note",
        ]

        if context["triage"] is not None:
            answer = (
                f"The latest triage result is "
                f"{context['triage'].final_urgency}. "
                f"The model originally predicted "
                f"{context['triage'].predicted_urgency} with "
                f"{round(context['triage'].confidence * 100)}% confidence. "
                f"Risk score is "
                f"{round(context['triage'].risk_score * 100)}%. "
                f"Explanation: {context['triage'].explanation}"
            )
        else:
            answer = (
                "No triage prediction has been generated for this referral yet."
            )

    elif (
        "dna" in question_lower
        or "miss appointment" in question_lower
        or "missed appointment" in question_lower
        or "attend" in question_lower
    ):
        sources = [
            "DNA prediction result",
            "Appointment risk features",
        ]

        if context["dna"] is not None:
            answer = (
                f"The latest DNA missed appointment risk is "
                f"{context['dna'].dna_risk}. "
                f"Confidence is {round(context['dna'].confidence * 100)}%. "
                f"Risk score is {round(context['dna'].risk_score * 100)}%. "
                f"Recommended action: {context['dna'].recommended_action}"
            )
        else:
            answer = (
                "No DNA missed appointment prediction has been generated "
                "for this referral yet."
            )

    elif (
        "review" in question_lower
        or "clinician" in question_lower
        or "doctor" in question_lower
        or "approved" in question_lower
    ):
        sources = [
            "Clinician review",
            "Referral status",
        ]

        if context["review"] is not None:
            answer = (
                f"The latest clinician review was completed by "
                f"{context['review'].reviewer_name}. "
                f"Decision: {context['review'].decision}. "
                f"Final urgency: {context['review'].final_urgency}. "
                f"Notes: {context['review'].notes}"
            )
        else:
            answer = (
                "No clinician review has been recorded for this referral yet."
            )

    elif (
        "next" in question_lower
        or "action" in question_lower
        or "what should" in question_lower
    ):
        sources = [
            "Triage result",
            "DNA result",
            "Red-flag assessment",
            "Clinician review",
        ]

        answer = ""

        if context["triage"] is not None:
            answer += (
                f"Clinical priority: {context['triage'].final_urgency}. "
            )

        if context["red_flag_detected"]:
            answer += (
                "Because a red flag is present, clinical review should be prioritised. "
            )

        if context["dna"] is not None:
            answer += (
                f"For appointment management, DNA recommendation is: "
                f"{context['dna'].recommended_action} "
            )

        if context["review"] is not None:
            answer += (
                f"The clinician decision is already recorded as "
                f"{context['review'].decision}. "
            )
        else:
            answer += "A clinician review should be completed before final action."

    else:
        sources = [
            "Referral note",
            "Extracted information",
            "Risk results",
        ]

        answer = (
            "I can answer questions about this referral summary, red flags, "
            "triage urgency, DNA missed appointment risk, clinician review, "
            "and suggested next actions. "
            "For this referral: "
            + create_summary_answer(context)
        )

    return {
        "answer": answer,
        "sources": sources,
    }