from sqlalchemy.orm import Session

from ..models import AuditLog


def create_audit_log(
    db: Session,
    referral_id: int,
    patient_id: str,
    action: str,
    details: str,
    source: str = "SYSTEM",
) -> AuditLog:
    audit_log = AuditLog(
        referral_id=referral_id,
        patient_id=patient_id,
        action=action,
        source=source,
        details=details,
    )

    db.add(audit_log)

    return audit_log