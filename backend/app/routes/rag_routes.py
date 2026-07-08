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
from ..schemas import RagAnswerRead, RagQuestionCreate
from ..services.audit_service import create_audit_log
from ..services.rag_service import (
    answer_question,
    build_referral_context,
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG Assistant"],
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


@router.post(
    "/referral/{referral_id}/ask",
    response_model=RagAnswerRead,
)
def ask_referral_assistant(
    referral_id: int,
    question_data: RagQuestionCreate,
    db: Session = Depends(get_db),
) -> RagAnswerRead:
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

    context = build_referral_context(
        referral=referral,
        latest_triage=latest_triage,
        latest_dna=latest_dna,
        latest_review=latest_review,
    )

    assistant_result = answer_question(
        question=question_data.question,
        context=context,
    )

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="RAG_ASSISTANT_USED",
        source="RAG_ASSISTANT",
        details=(
            "Referral assistant answered question: "
            + question_data.question
        ),
    )

    db.commit()

    return RagAnswerRead(
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        question=question_data.question,
        answer=assistant_result["answer"],
        sources=assistant_result["sources"],
        safety_note=(
            "This assistant provides decision-support explanations only. "
            "It must not be used as a final clinical decision-maker."
        ),
    )