import json
import os
import urllib.error
import urllib.request
from typing import Any


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2",
)


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


def build_context_text(
    referral,
    latest_triage,
    latest_dna,
    latest_review,
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
        else "No symptoms extracted"
    )

    condition_text = (
        ", ".join(conditions)
        if conditions
        else "No conditions extracted"
    )

    context = f"""
Patient ID: {referral.patient.patient_id}
Age: {referral.patient.age}
Gender: {referral.patient.gender}
Department: {referral.department}
Waiting days: {referral.waiting_days}
Referral status: {referral.status}

Referral note:
{referral.referral_text}

Extracted symptoms:
{symptom_text}

Extracted conditions:
{condition_text}

Duration:
{referral.duration_days if referral.duration_days is not None else "Not detected"}

Red flag detected:
{referral.red_flag_detected}

Red flag score:
{referral.red_flag_score}

Red flag reason:
{referral.red_flag_reason}
"""

    if latest_triage is not None:
        context += f"""

Latest triage result:
Predicted urgency: {latest_triage.predicted_urgency}
Final urgency: {latest_triage.final_urgency}
Confidence: {latest_triage.confidence}
Risk score: {latest_triage.risk_score}
Model: {latest_triage.model_name}
Explanation: {latest_triage.explanation}
"""
    else:
        context += """

Latest triage result:
Not generated yet.
"""

    if latest_dna is not None:
        context += f"""

Latest DNA missed appointment result:
DNA risk: {latest_dna.dna_risk}
Confidence: {latest_dna.confidence}
Risk score: {latest_dna.risk_score}
Recommended action: {latest_dna.recommended_action}
Model: {latest_dna.model_name}
"""
    else:
        context += """

Latest DNA missed appointment result:
Not generated yet.
"""

    if latest_review is not None:
        context += f"""

Latest clinician review:
Reviewer: {latest_review.reviewer_name}
Decision: {latest_review.decision}
Final urgency: {latest_review.final_urgency}
Notes: {latest_review.notes}
"""
    else:
        context += """

Latest clinician review:
Not recorded yet.
"""

    return context.strip()


def build_slm_prompt(context_text: str) -> str:
    return f"""
You are a healthcare decision-support assistant for a synthetic NHS-style referral triage prototype.

Your task:
Create a clear, concise referral summary for hospital staff.

Rules:
- Do not diagnose.
- Do not invent new clinical facts.
- Use only the provided referral context.
- Mention that clinician review is required.
- Keep the answer understandable and professional.

Referral context:
{context_text}

Write the summary using these headings:
1. Patient Overview
2. Key Symptoms and Conditions
3. Red-Flag and Triage Interpretation
4. DNA Missed Appointment Risk
5. Clinician Review Status
6. Recommended Next Step
""".strip()


def call_local_ollama(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
        },
    }

    request_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=request_data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=40,
    ) as response:
        response_data = response.read().decode("utf-8")

    decoded_response = json.loads(response_data)

    return decoded_response.get(
        "response",
        "",
    ).strip()


def create_fallback_summary(
    referral,
    latest_triage,
    latest_dna,
    latest_review,
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
        else "no extracted symptoms"
    )

    condition_text = (
        ", ".join(conditions)
        if conditions
        else "no extracted existing conditions"
    )

    summary = (
        f"Patient {referral.patient.patient_id} is a "
        f"{referral.patient.age}-year-old {referral.patient.gender} "
        f"patient referred to {referral.department}. "
        f"The referral note states: {referral.referral_text} "
        f"Extracted symptoms include {symptom_text}. "
        f"Extracted conditions include {condition_text}. "
    )

    if referral.red_flag_detected:
        summary += (
            f"A red flag was detected with score "
            f"{round(referral.red_flag_score * 100)}%. "
            f"Reason: {referral.red_flag_reason}. "
        )
    else:
        summary += (
            "No configured red-flag combination was detected. "
        )

    if latest_triage is not None:
        summary += (
            f"The latest triage result is "
            f"{latest_triage.final_urgency}, with "
            f"{round(latest_triage.confidence * 100)}% confidence. "
        )
    else:
        summary += (
            "No triage prediction has been generated yet. "
        )

    if latest_dna is not None:
        summary += (
            f"The latest DNA missed appointment risk is "
            f"{latest_dna.dna_risk}. Recommended action: "
            f"{latest_dna.recommended_action} "
        )
    else:
        summary += (
            "No DNA missed appointment prediction has been generated yet. "
        )

    if latest_review is not None:
        summary += (
            f"The latest clinician review decision is "
            f"{latest_review.decision}, with final urgency "
            f"{latest_review.final_urgency}. "
        )
    else:
        summary += (
            "No clinician review has been recorded yet. "
        )

    summary += (
        "This is a decision-support summary only. "
        "Final decisions require clinician review."
    )

    return summary


def generate_slm_summary(
    referral,
    latest_triage,
    latest_dna,
    latest_review,
) -> dict[str, Any]:
    context_text = build_context_text(
        referral=referral,
        latest_triage=latest_triage,
        latest_dna=latest_dna,
        latest_review=latest_review,
    )

    prompt = build_slm_prompt(
        context_text=context_text,
    )

    try:
        summary = call_local_ollama(prompt)

        if summary:
            return {
                "generated_by": f"Local SLM via Ollama ({OLLAMA_MODEL})",
                "summary": summary,
            }

    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        TimeoutError,
        json.JSONDecodeError,
        OSError,
    ):
        pass

    fallback_summary = create_fallback_summary(
        referral=referral,
        latest_triage=latest_triage,
        latest_dna=latest_dna,
        latest_review=latest_review,
    )

    return {
        "generated_by": "CareFlow fallback summary engine",
        "summary": fallback_summary,
    }