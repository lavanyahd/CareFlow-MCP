from .audit_routes import router as audit_router
from .patient_routes import router as patient_router
from .referral_routes import router as referral_router
from .triage_routes import router as triage_router
from .audit_routes import router as audit_router
from .dna_routes import router as dna_router
from .waiting_list_routes import router as waiting_list_router

__all__ = [
    "audit_router",
    "patient_router",
    "referral_router",
    "triage_router",
    "dna_router",
    "waiting_list_router",
]