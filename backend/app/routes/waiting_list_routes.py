from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import DNAResult, Referral, TriageResult
from ..schemas import WaitingListItemRead
from ..services.priority_score import (
    calculate_priority_score,
    get_suggested_action,
)


router = APIRouter(
    prefix="/waiting-list",
    tags=["Waiting List"],
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
    "",
    response_model=list[WaitingListItemRead],
)
def get_waiting_list(
    db: Session = Depends(get_db),
) -> list[WaitingListItemRead]:
    statement = (
        select(Referral)
        .options(joinedload(Referral.patient))
        .order_by(Referral.created_at.desc())
    )

    referrals = db.scalars(statement).all()

    waiting_list_items = []

    for referral in referrals:
        latest_triage = get_latest_triage_result(
            db=db,
            referral_id=referral.id,
        )

        latest_dna = get_latest_dna_result(
            db=db,
            referral_id=referral.id,
        )

        if latest_triage is not None:
            triage_urgency = latest_triage.final_urgency
            triage_risk_score = latest_triage.risk_score
        else:
            triage_urgency = "Not predicted"
            triage_risk_score = referral.red_flag_score

        if latest_dna is not None:
            dna_risk = latest_dna.dna_risk
            dna_risk_score = latest_dna.risk_score
            dna_recommended_action = latest_dna.recommended_action
        else:
            dna_risk = "Not predicted"
            dna_risk_score = 0.0
            dna_recommended_action = "DNA risk not predicted yet."

        priority_score = calculate_priority_score(
            triage_risk_score=triage_risk_score,
            waiting_days=referral.waiting_days,
            red_flag_score=referral.red_flag_score,
            final_urgency=triage_urgency,
        )

        suggested_action = get_suggested_action(
            final_urgency=triage_urgency,
            priority_score=priority_score,
            red_flag_detected=referral.red_flag_detected,
        )

        waiting_list_items.append(
            WaitingListItemRead(
                referral_id=referral.id,
                patient_id=referral.patient.patient_id,
                age=referral.patient.age,
                gender=referral.patient.gender,
                department=referral.department,
                waiting_days=referral.waiting_days,
                referral_text=referral.referral_text,
                red_flag_detected=referral.red_flag_detected,
                red_flag_score=referral.red_flag_score,
                triage_urgency=triage_urgency,
                triage_risk_score=triage_risk_score,
                priority_score=priority_score,
                suggested_action=suggested_action,
                dna_risk=dna_risk,
                dna_risk_score=dna_risk_score,
                dna_recommended_action=dna_recommended_action,
                status=referral.status,
                created_at=referral.created_at,
            )
        )

    waiting_list_items.sort(
        key=lambda item: item.priority_score,
        reverse=True,
    )

    return waiting_list_items