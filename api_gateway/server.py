
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTERS
from api_gateway.routes.pricing_routes import router as pricing_router
from api_gateway.routes.matrix_routes import router as matrix_router
from api_gateway.routes.config_routes import router as config_router
from api_gateway.routes.admin_pricing_dashboard import router as admin_router

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
