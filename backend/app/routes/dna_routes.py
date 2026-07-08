from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import DNAResult, Referral
from ..schemas import DNAResultRead
from ..services.audit_service import create_audit_log
from ..services.dna_service import predict_dna


router = APIRouter(
    prefix="/dna",
    tags=["DNA Prediction"],
)


@router.post(
    "/predict/{referral_id}",
    response_model=DNAResultRead,
    status_code=status.HTTP_201_CREATED,
)
def predict_referral_dna(
    referral_id: int,
    db: Session = Depends(get_db),
) -> DNAResult:
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

    prediction = predict_dna(referral)

    dna_result = DNAResult(
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        dna_risk=prediction["dna_risk"],
        risk_score=prediction["risk_score"],
        confidence=prediction["confidence"],
        appointment_day=prediction["appointment_day"],
        appointment_time=prediction["appointment_time"],
        distance_band=prediction["distance_band"],
        previous_missed_appointments=prediction[
            "previous_missed_appointments"
        ],
        previous_cancellations=prediction[
            "previous_cancellations"
        ],
        reminder_sent=prediction["reminder_sent"],
        recommended_action=prediction["recommended_action"],
        model_name=prediction["model_name"],
    )

    db.add(dna_result)

    confidence_percent = round(
        prediction["confidence"] * 100
    )

    risk_score_percent = round(
        prediction["risk_score"] * 100
    )

    audit_details = (
        "DNA risk predicted as "
        + prediction["dna_risk"]
        + ". Confidence: "
        + str(confidence_percent)
        + "%. Risk score: "
        + str(risk_score_percent)
        + "%. Recommended action: "
        + prediction["recommended_action"]
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="DNA_RISK_PREDICTED",
        source="ML_MODEL",
        details=audit_details,
    )

    db.commit()
    db.refresh(dna_result)

    return dna_result


@router.get(
    "/results/{referral_id}",
    response_model=list[DNAResultRead],
)
def get_dna_results(
    referral_id: int,
    db: Session = Depends(get_db),
) -> list[DNAResult]:
    statement = (
        select(DNAResult)
        .where(DNAResult.referral_id == referral_id)
        .order_by(DNAResult.created_at.desc())
    )

    dna_results = db.scalars(statement).all()

    return list(dna_results)