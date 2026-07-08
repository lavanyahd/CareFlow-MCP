import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Patient, Referral
from ..schemas import ReferralCreate, ReferralRead
from ..services.audit_service import create_audit_log
from ..services.red_flag_rules import evaluate_red_flags
from ..services.referral_parser import parse_referral_note


router = APIRouter(
    prefix="/referrals",
    tags=["Referrals"],
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


def format_referral(referral: Referral) -> ReferralRead:
    return ReferralRead(
        id=referral.id,
        patient_id=referral.patient.patient_id,
        age=referral.patient.age,
        gender=referral.patient.gender,
        department=referral.department,
        waiting_days=referral.waiting_days,
        referral_text=referral.referral_text,
        extracted_symptoms=decode_json_list(referral.extracted_symptoms),
        extracted_conditions=decode_json_list(referral.extracted_conditions),
        duration_days=referral.duration_days,
        red_flag_detected=referral.red_flag_detected,
        red_flag_score=referral.red_flag_score,
        red_flag_reason=referral.red_flag_reason,
        status=referral.status,
        created_at=referral.created_at,
    )


@router.post(
    "",
    response_model=ReferralRead,
    status_code=status.HTTP_201_CREATED,
)
def create_referral(
    referral_data: ReferralCreate,
    db: Session = Depends(get_db),
) -> ReferralRead:
    patient = db.scalar(
        select(Patient).where(
            Patient.patient_id == referral_data.patient_id
        )
    )

    if patient is None:
        patient = Patient(
            patient_id=referral_data.patient_id,
            age=referral_data.age,
            gender=referral_data.gender,
        )

        db.add(patient)
        db.flush()

    else:
        patient.age = referral_data.age
        patient.gender = referral_data.gender

    parsed_referral = parse_referral_note(
        referral_data.referral_text
    )

    red_flag_result = evaluate_red_flags(
        age=referral_data.age,
        symptoms=parsed_referral["symptoms"],
        conditions=parsed_referral["conditions"],
    )

    referral = Referral(
        patient_pk=patient.id,
        department=referral_data.department,
        waiting_days=referral_data.waiting_days,
        referral_text=referral_data.referral_text,
        extracted_symptoms=json.dumps(
            parsed_referral["symptoms"]
        ),
        extracted_conditions=json.dumps(
            parsed_referral["conditions"]
        ),
        duration_days=parsed_referral["duration_days"],
        red_flag_detected=red_flag_result[
            "red_flag_detected"
        ],
        red_flag_score=red_flag_result[
            "red_flag_score"
        ],
        red_flag_reason=red_flag_result[
            "red_flag_reason"
        ],
    )

    db.add(referral)

    # This creates the referral ID before final commit,
    # so audit logs can use referral.id.
    db.flush()

    symptoms_text = (
        ", ".join(parsed_referral["symptoms"])
        if parsed_referral["symptoms"]
        else "None detected"
    )

    conditions_text = (
        ", ".join(parsed_referral["conditions"])
        if parsed_referral["conditions"]
        else "None detected"
    )

    duration_text = (
        f'{parsed_referral["duration_days"]} days'
        if parsed_referral["duration_days"] is not None
        else "Not detected"
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral_data.patient_id,
        action="REFERRAL_CREATED",
        source="STAFF_PORTAL",
        details=(
            f"Referral submitted to "
            f"{referral_data.department}. "
            f"Waiting days: {referral_data.waiting_days}."
        ),
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral_data.patient_id,
        action="REFERRAL_PARSED",
        source="SYSTEM",
        details=(
            f"Symptoms extracted: {symptoms_text}. "
            f"Conditions extracted: {conditions_text}. "
            f"Duration: {duration_text}."
        ),
    )

    if red_flag_result["red_flag_detected"]:
        create_audit_log(
            db=db,
            referral_id=referral.id,
            patient_id=referral_data.patient_id,
            action="RED_FLAG_DETECTED",
            source="SYSTEM",
            details=(
                f'Score: '
                f'{red_flag_result["red_flag_score"]:.2f}. '
                f'Reason: '
                f'{red_flag_result["red_flag_reason"]}'
            ),
        )

    else:
        create_audit_log(
            db=db,
            referral_id=referral.id,
            patient_id=referral_data.patient_id,
            action="RED_FLAG_CHECK_COMPLETED",
            source="SYSTEM",
            details=(
                "No configured red-flag combination "
                "was detected."
            ),
        )

    db.commit()
    db.refresh(referral)

    referral.patient = patient

    return format_referral(referral)


@router.get(
    "",
    response_model=list[ReferralRead],
)
def get_all_referrals(
    db: Session = Depends(get_db),
) -> list[ReferralRead]:
    statement = (
        select(Referral)
        .options(joinedload(Referral.patient))
        .order_by(Referral.created_at.desc())
    )

    referrals = db.scalars(statement).all()

    return [
        format_referral(referral)
        for referral in referrals
    ]


@router.get(
    "/{referral_id}",
    response_model=ReferralRead,
)
def get_referral(
    referral_id: int,
    db: Session = Depends(get_db),
) -> ReferralRead:
    statement = (
        select(Referral)
        .options(joinedload(Referral.patient))
        .where(Referral.id == referral_id)
    )

    referral = db.scalar(statement)

    if referral is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referral not found.",
        )

    return format_referral(referral)