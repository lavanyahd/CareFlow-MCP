from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Referral, TriageResult
from ..schemas import TriageResultRead
from ..services.audit_service import create_audit_log
from ..services.triage_service import predict_triage


router = APIRouter(
    prefix="/triage",
    tags=["Triage"],
)


@router.post(
    "/predict/{referral_id}",
    response_model=TriageResultRead,
    status_code=status.HTTP_201_CREATED,
)
def predict_referral_triage(
    referral_id: int,
    db: Session = Depends(get_db),
) -> TriageResult:
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

    prediction = predict_triage(referral)

    triage_result = TriageResult(
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        predicted_urgency=prediction["predicted_urgency"],
        final_urgency=prediction["final_urgency"],
        risk_score=prediction["risk_score"],
        confidence=prediction["confidence"],
        human_review_required=prediction["human_review_required"],
        explanation=prediction["explanation"],
        model_name=prediction["model_name"],
    )

    db.add(triage_result)

    confidence_percent = round(
        prediction["confidence"] * 100
    )

    risk_score_percent = round(
        prediction["risk_score"] * 100
    )

    audit_details = (
        "Predicted urgency: "
        + prediction["predicted_urgency"]
        + ". Final urgency: "
        + prediction["final_urgency"]
        + ". Confidence: "
        + str(confidence_percent)
        + "%. Risk score: "
        + str(risk_score_percent)
        + "%."
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="TRIAGE_PREDICTED",
        source="ML_MODEL",
        details=audit_details,
    )

    db.commit()
    db.refresh(triage_result)

    return triage_result


@router.get(
    "/results/{referral_id}",
    response_model=list[TriageResultRead],
)
def get_triage_results(
    referral_id: int,
    db: Session = Depends(get_db),
) -> list[TriageResult]:
    statement = (
        select(TriageResult)
        .where(TriageResult.referral_id == referral_id)
        .order_by(TriageResult.created_at.desc())
    )

    triage_results = db.scalars(statement).all()

    return list(triage_results)