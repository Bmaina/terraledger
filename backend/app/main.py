from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router

app = FastAPI(
    title="TerraLedger API",
    description=(
        "Geo-Verified Supply Chain Compliance for the EU Deforestation Regulation (EUDR). "
        "Plot-level satellite deforestation scoring + chain of custody + DDS generation."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "name": "TerraLedger",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }
