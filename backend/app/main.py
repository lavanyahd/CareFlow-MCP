from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine

from .routes.audit_routes import router as audit_router
from .routes.dna_routes import router as dna_router
from .routes.patient_routes import router as patient_router
from .routes.referral_routes import router as referral_router
from .routes.triage_routes import router as triage_router
from .routes.waiting_list_routes import router as waiting_list_router
from .routes.review_routes import router as review_router
from .routes.report_routes import router as report_router
from .routes.fhir_routes import router as fhir_router
from .routes.monitoring_routes import router as monitoring_router
from .routes.rag_routes import router as rag_router
from .routes.slm_routes import router as slm_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.app_name,
    description="NHS-style referral triage and patient-flow optimisation prototype.",
    version="0.1.0",
)


allowed_origins = [
    settings.frontend_url,
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    referral_router,
    prefix="/api",
)

app.include_router(
    patient_router,
    prefix="/api",
)

app.include_router(
    audit_router,
    prefix="/api",
)

app.include_router(
    triage_router,
    prefix="/api",
)

app.include_router(
    waiting_list_router,
    prefix="/api",
)

app.include_router(
    dna_router,
    prefix="/api",
)

app.include_router(
    review_router,
    prefix="/api",
)

app.include_router(
    report_router,
    prefix="/api",
)

app.include_router(
    fhir_router,
    prefix="/api",
)

app.include_router(
    monitoring_router,
    prefix="/api",
)

app.include_router(
    rag_router,
    prefix="/api",
)

app.include_router(
    slm_router,
    prefix="/api",
)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": settings.app_name,
        "environment": settings.environment,
    }