"""Cloudry FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.logging_config import get_logger, setup_logging
from src.middleware.rate_limiter import limiter
from src.routers import hash, image, markdown, pdf, qr, text

setup_logging()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Cloudry API starting", extra={"environment": settings.environment})
    yield
    logger.info("Cloudry API shutting down")


app = FastAPI(
    title="Cloudry API",
    description="Free online utilities — PDF, Image, QR, and file tools.",
    version="0.1.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Rate limiting
app.state.limiter = limiter


# Health endpoints
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "cloudry-api", "version": "0.1.0"}


@app.get("/_admin/health/liveness")
async def liveness():
    """Liveness probe for orchestrators."""
    return {"status": "alive"}


@app.get("/_admin/health/readiness")
async def readiness():
    """Readiness probe for orchestrators."""
    return {"status": "ready"}


# Register routers
app.include_router(pdf.router, prefix="/api/v1/pdf", tags=["PDF Tools"])
app.include_router(image.router, prefix="/api/v1/image", tags=["Image Tools"])
app.include_router(qr.router, prefix="/api/v1/qr", tags=["QR Tools"])
app.include_router(hash.router, prefix="/api/v1/hash", tags=["Hash Tools"])
app.include_router(markdown.router, prefix="/api/v1/markdown", tags=["Markdown Tools"])
app.include_router(text.router, prefix="/api/v1/text", tags=["Text Tools"])
