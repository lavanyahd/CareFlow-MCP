from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Patient
from ..schemas import PatientRead


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.get(
    "/{patient_id}",
    response_model=PatientRead,
)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
) -> Patient:
    patient = db.scalar(
        select(Patient).where(
            Patient.patient_id == patient_id
        )
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return patient