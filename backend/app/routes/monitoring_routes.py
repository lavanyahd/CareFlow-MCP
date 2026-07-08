from fastapi import APIRouter

from ..services.monitoring_service import (
    get_model_monitoring_summary,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["Model Monitoring"],
)


@router.get("/models")
def get_model_monitoring():
    return get_model_monitoring_summary()