from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import (
    ClinicianReview,
    DNAResult,
    Referral,
    TriageResult,
)
from ..services.audit_service import create_audit_log
from ..services.report_generator import generate_referral_report


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
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


def get_reviews(
    db: Session,
    referral_id: int,
) -> list[ClinicianReview]:
    statement = (
        select(ClinicianReview)
        .where(ClinicianReview.referral_id == referral_id)
        .order_by(ClinicianReview.created_at.desc())
    )

    return list(db.scalars(statement).all())


@router.get(
    "/referral/{referral_id}",
    response_class=FileResponse,
)
def download_referral_report(
    referral_id: int,
    db: Session = Depends(get_db),
):
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

    reviews = get_reviews(
        db=db,
        referral_id=referral.id,
    )

    report_path = generate_referral_report(
        referral=referral,
        latest_triage=latest_triage,
        latest_dna=latest_dna,
        reviews=reviews,
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="REPORT_GENERATED",
        source="SYSTEM",
        details="PDF referral decision-support report generated.",
    )

    db.commit()

    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename=f"careflow_referral_{referral.id}_report.pdf",
    )