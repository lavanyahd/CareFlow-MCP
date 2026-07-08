from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import ClinicianReview, Referral
from ..schemas import ClinicianReviewCreate, ClinicianReviewRead
from ..services.audit_service import create_audit_log


router = APIRouter(
    prefix="/reviews",
    tags=["Clinician Review"],
)


@router.post(
    "/{referral_id}",
    response_model=ClinicianReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_clinician_review(
    referral_id: int,
    review_data: ClinicianReviewCreate,
    db: Session = Depends(get_db),
) -> ClinicianReview:
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

    review = ClinicianReview(
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        reviewer_name=review_data.reviewer_name,
        decision=review_data.decision,
        final_urgency=review_data.final_urgency,
        notes=review_data.notes,
    )

    db.add(review)

    if review_data.decision.lower() == "request more information":
        referral.status = "More Information Required"
    else:
        referral.status = "Clinician Reviewed"

    create_audit_log(
        db=db,
        referral_id=referral.id,
        patient_id=referral.patient.patient_id,
        action="CLINICIAN_REVIEWED",
        source="CLINICIAN",
        details=(
            "Review completed by "
            + review_data.reviewer_name
            + ". Decision: "
            + review_data.decision
            + ". Final urgency: "
            + review_data.final_urgency
            + ". Notes: "
            + review_data.notes
        ),
    )

    db.commit()
    db.refresh(review)

    return review


@router.get(
    "/{referral_id}",
    response_model=list[ClinicianReviewRead],
)
def get_clinician_reviews(
    referral_id: int,
    db: Session = Depends(get_db),
) -> list[ClinicianReview]:
    statement = (
        select(ClinicianReview)
        .where(ClinicianReview.referral_id == referral_id)
        .order_by(ClinicianReview.created_at.desc())
    )

    reviews = db.scalars(statement).all()

    return list(reviews)