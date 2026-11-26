
import logging
import os
import tempfile
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.matrix_loader import PROJECT_ROOT, load_matrix, resolve_matrix_path
from shared.engine_registry import refresh_engines

# ROUTERS
from api_gateway.routes.pricing_routes import router as pricing_router
from api_gateway.routes.matrix_routes import router as matrix_router
from api_gateway.routes.config_routes import router as config_router
from api_gateway.routes.admin_pricing_dashboard import router as admin_router
from api_gateway.routes.owner_activity_routes import router as owner_activity_router

# MIDDLEWARE
from api_gateway.middleware.logging_middleware import LoggingMiddleware


# ---------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("genxbaby-pricing-engine")

app = FastAPI(
    title="GenXBaby Pricing Engine Gateway",
    description="GenXBaby pricing, matrix, configuration and admin API",
    version="1.1.0"
)


# ---------------------------------------------------------
# AUTHORIZED FRONTEND DOMAINS
# ---------------------------------------------------------

origins = [
    # Production frontend
    "https://genxbaby-admin-frontend.vercel.app",

    # Vercel preview deployments
    "https://genxbaby-admin-frontend-1qld-eei80eamx-millionmike3s-projects.vercel.app",
    "https://genxbaby-admin-frontend-1qld-bqmcqdmtv-millionmike3s-projects.vercel.app",
    "https://genxbaby-admin-frontend-1qld-ih9t1g8q4-millionmike3s-projects.vercel.app",
    "https://genxbaby-admin-frontend-1qld-qsc3smeo1-millionmike3s-projects.vercel.app",
    "https://gx-pricing-engine-fftl1pnkk-millionmike3s-projects.vercel.app",
    "https://gx-pricing-engine-902nzhdn8-millionmike3s-projects.vercel.app",

    # Vercel team domain
    "https://millionmike3s-projects.vercel.app",

    # Local development
    "http://localhost:3000",
]


# ---------------------------------------------------------
# LOGGING MIDDLEWARE
# ---------------------------------------------------------

# Register logging first.
# CORS will be registered last and will wrap this middleware.
app.add_middleware(LoggingMiddleware)


# ---------------------------------------------------------
# CORS MIDDLEWARE
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,

    allow_origins=origins,

    # Allow matching preview deployments for this frontend project.
    allow_origin_regex=(
        r"^https://genxbaby-admin-frontend-[a-z0-9-]+"
        r"-millionmike3s-projects\.vercel\.app$"
    ),

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],

    expose_headers=[
        "Content-Length",
        "Content-Type",
    ],

    max_age=600,
)


# ---------------------------------------------------------
# API ROUTERS
# ---------------------------------------------------------

app.include_router(
    pricing_router,
    prefix="/pricing"
)

app.include_router(
    matrix_router,
    prefix="/matrix"
)

app.include_router(
    config_router,
    prefix="/config"
)

app.include_router(
    admin_router,
    prefix="/admin"
)

# Owner pricing activity routes use complete paths and no prefix.
app.include_router(owner_activity_router)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GenXBaby Pricing Engine Gateway",
        "version": "1.1.0"
    }


# ---------------------------------------------------------
# MATRIX HEALTH CHECK
# ---------------------------------------------------------

@app.get("/matrix-status")
async def matrix_status():
    return {
        "status": "online",
        "service": "GenXBaby Pricing Matrix",
        "endpoint": "/matrix/current"
    }


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "GenXBaby Pricing Engine Gateway is running",
        "status": "online",
        "version": "1.1.0",
        "endpoints": {
            "health": "/health",
            "pricing": "/pricing",
            "matrix": "/matrix/current",
            "matrix_status": "/matrix-status",
            "configuration": "/config",
            "admin": "/admin",
            "documentation": "/docs"
        }
    }


@app.on_event("startup")
async def initialize_pricing_matrix_storage():
    """Initialize persistent matrix storage without overwriting existing data."""
    matrix_path = resolve_matrix_path()
    seed_path = PROJECT_ROOT / "data" / "pricing_matrix.json"

    if matrix_path.exists():
        load_matrix(matrix_path)
        refresh_engines(matrix_path)
        logger.info("Loaded existing pricing matrix from %s", matrix_path)
        return

    if not seed_path.is_file():
        raise RuntimeError(
            f"Pricing matrix is missing from both persistent storage "
            f"and the application seed: {matrix_path}"
        )

    load_matrix(seed_path)
    matrix_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = None
    try:
        seed_bytes = seed_path.read_bytes()

        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix="pricing_matrix_init_",
            suffix=".json",
            dir=str(matrix_path.parent),
            delete=False,
        ) as temp_file:
            temp_file.write(seed_bytes)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            temp_path = Path(temp_file.name)

        if matrix_path.exists():
            load_matrix(matrix_path)
        else:
            os.replace(temp_path, matrix_path)
            temp_path = None

        load_matrix(matrix_path)
        refresh_engines(matrix_path)
        logger.info("Initialized persistent pricing matrix at %s", matrix_path)

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
