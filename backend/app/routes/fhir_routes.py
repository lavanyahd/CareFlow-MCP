from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import DNAResult, Referral, TriageResult
from ..services.audit_service import create_audit_log
from ..services.fhir_service import build_fhir_bundle


router = APIRouter(
    prefix="/fhir",
    tags=["FHIR"],
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


@router.get(
    "/referral/{referral_id}",
)
def get_referral_fhir_bundle(
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

    fhir_bundle = build_fhir_bundle(
        referral=referral,
        latest_triage=latest_triage,
        latest_dna=latest_dna,
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="FHIR_VIEWED",
        source="SYSTEM",
        details="FHIR mock referral bundle viewed.",
    )

    db.commit()

    return fhir_bundle