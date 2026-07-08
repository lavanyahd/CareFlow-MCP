from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def current_utc_time() -> datetime:
    return datetime.now(timezone.utc)


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )

    referrals: Mapped[list["Referral"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
    )


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_pk: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    waiting_days: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    referral_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    extracted_symptoms: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    extracted_conditions: Mapped[str] = mapped_column(
        Text,
        default="[]",
        nullable=False,
    )

    duration_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    red_flag_detected: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    red_flag_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    red_flag_reason: Mapped[str] = mapped_column(
        Text,
        default="No red flags detected.",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Pending Review",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )

    patient: Mapped["Patient"] = relationship(
        back_populates="referrals",
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    referral_id: Mapped[int] = mapped_column(
        ForeignKey("referrals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        default="SYSTEM",
        nullable=False,
    )

    details: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )

class TriageResult(Base):
    __tablename__ = "triage_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    referral_id: Mapped[int] = mapped_column(
        ForeignKey("referrals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    predicted_urgency: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    final_urgency: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    human_review_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )

class DNAResult(Base):
    __tablename__ = "dna_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    referral_id: Mapped[int] = mapped_column(
        ForeignKey("referrals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    dna_risk: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    appointment_day: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    appointment_time: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    distance_band: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    previous_missed_appointments: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    previous_cancellations: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    reminder_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    recommended_action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )    

class ClinicianReview(Base):
    __tablename__ = "clinician_reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    referral_id: Mapped[int] = mapped_column(
        ForeignKey("referrals.id"),
        nullable=False,
        index=True,
    )

    patient_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    reviewer_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    decision: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    final_urgency: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    notes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_utc_time,
        nullable=False,
    )    