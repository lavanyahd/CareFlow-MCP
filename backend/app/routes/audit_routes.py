from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AuditLog
from ..schemas import AuditLogRead


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=list[AuditLogRead],
)
def get_audit_logs(
    referral_id: int | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
) -> list[AuditLog]:
    statement = (
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )

    if referral_id is not None:
        statement = statement.where(
            AuditLog.referral_id == referral_id
        )

    return list(db.scalars(statement).all())