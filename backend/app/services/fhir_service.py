import json
from datetime import datetime, timezone
from typing import Any


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


def create_fhir_patient_resource(referral) -> dict[str, Any]:
    return {
        "resourceType": "Patient",
        "id": referral.patient.patient_id,
        "identifier": [
            {
                "system": "https://careflow-mcp.local/patient-id",
                "value": referral.patient.patient_id,
            }
        ],
        "gender": referral.patient.gender.lower(),
        "extension": [
            {
                "url": "https://careflow-mcp.local/fhir/age",
                "valueInteger": referral.patient.age,
            }
        ],
    }


def create_fhir_service_request_resource(referral) -> dict[str, Any]:
    return {
        "resourceType": "ServiceRequest",
        "id": f"referral-{referral.id}",
        "status": "active",
        "intent": "order",
        "subject": {
            "reference": f"Patient/{referral.patient.patient_id}"
        },
        "category": [
            {
                "text": referral.department
            }
        ],
        "priority": "urgent" if referral.red_flag_detected else "routine",
        "authoredOn": referral.created_at.isoformat(),
        "reasonCode": [
            {
                "text": referral.referral_text
            }
        ],
        "note": [
            {
                "text": (
                    "Referral generated inside CareFlow-MCP "
                    "synthetic decision-support prototype."
                )
            }
        ],
    }


def create_fhir_symptom_observations(referral) -> list[dict[str, Any]]:
    symptoms = decode_json_list(referral.extracted_symptoms)

    observations = []

    for index, symptom in enumerate(symptoms, start=1):
        observations.append(
            {
                "resourceType": "Observation",
                "id": f"symptom-{referral.id}-{index}",
                "status": "final",
                "subject": {
                    "reference": f"Patient/{referral.patient.patient_id}"
                },
                "code": {
                    "text": "Extracted symptom"
                },
                "valueString": symptom,
            }
        )

    return observations


def create_fhir_condition_resources(referral) -> list[dict[str, Any]]:
    conditions = decode_json_list(referral.extracted_conditions)

    condition_resources = []

    for index, condition in enumerate(conditions, start=1):
        condition_resources.append(
            {
                "resourceType": "Condition",
                "id": f"condition-{referral.id}-{index}",
                "clinicalStatus": {
                    "text": "active"
                },
                "subject": {
                    "reference": f"Patient/{referral.patient.patient_id}"
                },
                "code": {
                    "text": condition
                },
            }
        )

    return condition_resources


def create_red_flag_observation(referral) -> dict[str, Any]:
    return {
        "resourceType": "Observation",
        "id": f"red-flag-{referral.id}",
        "status": "final",
        "subject": {
            "reference": f"Patient/{referral.patient.patient_id}"
        },
        "code": {
            "text": "CareFlow red-flag assessment"
        },
        "valueBoolean": referral.red_flag_detected,
        "component": [
            {
                "code": {
                    "text": "Red flag score"
                },
                "valueDecimal": referral.red_flag_score,
            },
            {
                "code": {
                    "text": "Red flag reason"
                },
                "valueString": referral.red_flag_reason,
            },
        ],
    }


def create_triage_observation(referral, latest_triage) -> dict[str, Any] | None:
    if latest_triage is None:
        return None

    return {
        "resourceType": "Observation",
        "id": f"triage-{latest_triage.id}",
        "status": "final",
        "subject": {
            "reference": f"Patient/{referral.patient.patient_id}"
        },
        "code": {
            "text": "CareFlow ML triage prediction"
        },
        "valueString": latest_triage.final_urgency,
        "component": [
            {
                "code": {
                    "text": "Predicted urgency"
                },
                "valueString": latest_triage.predicted_urgency,
            },
            {
                "code": {
                    "text": "Confidence"
                },
                "valueDecimal": latest_triage.confidence,
            },
            {
                "code": {
                    "text": "Risk score"
                },
                "valueDecimal": latest_triage.risk_score,
            },
            {
                "code": {
                    "text": "Model name"
                },
                "valueString": latest_triage.model_name,
            },
        ],
    }


def create_dna_observation(referral, latest_dna) -> dict[str, Any] | None:
    if latest_dna is None:
        return None

    return {
        "resourceType": "Observation",
        "id": f"dna-{latest_dna.id}",
        "status": "final",
        "subject": {
            "reference": f"Patient/{referral.patient.patient_id}"
        },
        "code": {
            "text": "CareFlow DNA missed appointment prediction"
        },
        "valueString": latest_dna.dna_risk,
        "component": [
            {
                "code": {
                    "text": "Confidence"
                },
                "valueDecimal": latest_dna.confidence,
            },
            {
                "code": {
                    "text": "Risk score"
                },
                "valueDecimal": latest_dna.risk_score,
            },
            {
                "code": {
                    "text": "Recommended action"
                },
                "valueString": latest_dna.recommended_action,
            },
            {
                "code": {
                    "text": "Model name"
                },
                "valueString": latest_dna.model_name,
            },
        ],
    }


def build_fhir_bundle(
    referral,
    latest_triage,
    latest_dna,
) -> dict[str, Any]:
    resources = []

    resources.append(
        create_fhir_patient_resource(referral)
    )

    resources.append(
        create_fhir_service_request_resource(referral)
    )

    resources.extend(
        create_fhir_symptom_observations(referral)
    )

    resources.extend(
        create_fhir_condition_resources(referral)
    )

    resources.append(
        create_red_flag_observation(referral)
    )

    triage_resource = create_triage_observation(
        referral=referral,
        latest_triage=latest_triage,
    )

    if triage_resource is not None:
        resources.append(triage_resource)

    dna_resource = create_dna_observation(
        referral=referral,
        latest_dna=latest_dna,
    )

    if dna_resource is not None:
        resources.append(dna_resource)

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "entry": [
            {
                "resource": resource
            }
            for resource in resources
        ],
    }