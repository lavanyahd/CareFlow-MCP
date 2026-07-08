from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import (
    ClinicianReview,
    DNAResult,
    Referral,
    TriageResult,
)
from ..schemas import SlmSummaryRead
from ..services.audit_service import create_audit_log
from ..services.slm_service import generate_slm_summary


router = APIRouter(
    prefix="/slm",
    tags=["SLM Summary"],
)


def get_latest_triage_result(
    db: Session,
    referral_id: int,
) -> TriageResult | None:
    statement = (
        select(TriageResult)
        .where(TriageResult.referral_id == referral_id)
        .order_by(TriageResult.created_at.desc())
    )

    return db.scalar(statement)


def get_latest_dna_result(
    db: Session,
    referral_id: int,
) -> DNAResult | None:
    statement = (
        select(DNAResult)
        .where(DNAResult.referral_id == referral_id)
        .order_by(DNAResult.created_at.desc())
    )

    return db.scalar(statement)


def get_latest_review(
    db: Session,
    referral_id: int,
) -> ClinicianReview | None:
    statement = (
        select(ClinicianReview)
        .where(ClinicianReview.referral_id == referral_id)
        .order_by(ClinicianReview.created_at.desc())
    )

    return db.scalar(statement)


@router.get(
    "/referral/{referral_id}/summary",
    response_model=SlmSummaryRead,
)
def get_slm_referral_summary(
    referral_id: int,
    db: Session = Depends(get_db),
) -> SlmSummaryRead:
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

    latest_triage = get_latest_triage_result(
        db=db,
        referral_id=referral.id,
    )

    latest_dna = get_latest_dna_result(
        db=db,
        referral_id=referral.id,
    )

    latest_review = get_latest_review(
        db=db,
        referral_id=referral.id,
    )

    slm_result = generate_slm_summary(
        referral=referral,
        latest_triage=latest_triage,
        latest_dna=latest_dna,
        latest_review=latest_review,
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="SLM_SUMMARY_GENERATED",
        source="SLM_SERVICE",
        details=(
            "SLM referral summary generated using "
            + slm_result["generated_by"]
            + "."
        ),
    )

    db.commit()

    return SlmSummaryRead(
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        generated_by=slm_result["generated_by"],
        summary=slm_result["summary"],
        safety_note=(
            "This summary is decision-support only. "
            "It must not be used as a final clinical decision."
        ),
    )