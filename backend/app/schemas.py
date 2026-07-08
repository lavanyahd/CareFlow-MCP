from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReferralCreate(BaseModel):
    patient_id: str = Field(
        min_length=1,
        max_length=50,
    )

    age: int = Field(
        ge=0,
        le=120,
    )

    gender: str = Field(
        min_length=1,
        max_length=30,
    )

    department: str = Field(
        min_length=2,
        max_length=100,
    )

    waiting_days: int = Field(
        default=0,
        ge=0,
        le=3650,
    )

    referral_text: str = Field(
        min_length=10,
        max_length=5000,
    )


class ReferralRead(BaseModel):
    id: int
    patient_id: str
    age: int
    gender: str
    department: str
    waiting_days: int
    referral_text: str

    extracted_symptoms: list[str] = Field(
        default_factory=list
    )

    extracted_conditions: list[str] = Field(
        default_factory=list
    )

    duration_days: int | None = None

    red_flag_detected: bool
    red_flag_score: float
    red_flag_reason: str

    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PatientRead(BaseModel):
    id: int
    patient_id: str
    age: int
    gender: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str

class AuditLogRead(BaseModel):
    id: int
    referral_id: int
    patient_id: str
    action: str
    source: str
    details: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TriageResultRead(BaseModel):
    id: int
    referral_id: int
    patient_id: str
    predicted_urgency: str
    final_urgency: str
    risk_score: float
    confidence: float
    human_review_required: bool
    explanation: str
    model_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WaitingListItemRead(BaseModel):
    referral_id: int
    patient_id: str
    age: int
    gender: str
    department: str
    waiting_days: int
    referral_text: str
    red_flag_detected: bool
    red_flag_score: float
    triage_urgency: str
    triage_risk_score: float
    priority_score: float
    suggested_action: str
    dna_risk: str
    dna_risk_score: float
    dna_recommended_action: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DNAResultRead(BaseModel):
    id: int
    referral_id: int
    patient_id: str
    dna_risk: str
    risk_score: float
    confidence: float
    appointment_day: str
    appointment_time: str
    distance_band: str
    previous_missed_appointments: int
    previous_cancellations: int
    reminder_sent: bool
    recommended_action: str
    model_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClinicianReviewCreate(BaseModel):
    reviewer_name: str = Field(min_length=2, max_length=100)
    decision: str = Field(min_length=2, max_length=100)
    final_urgency: str = Field(min_length=2, max_length=50)
    notes: str = Field(min_length=2, max_length=1000)


class ClinicianReviewRead(BaseModel):
    id: int
    referral_id: int
    patient_id: str
    reviewer_name: str
    decision: str
    final_urgency: str
    notes: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  

class RagQuestionCreate(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class RagAnswerRead(BaseModel):
    referral_id: int
    patient_id: str
    question: str
    answer: str
    sources: list[str]
    safety_note: str      

class SlmSummaryRead(BaseModel):
    referral_id: int
    patient_id: str
    generated_by: str
    summary: str
    safety_note: str    