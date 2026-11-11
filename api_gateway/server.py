
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTERS
from api_gateway.routes.pricing_routes import router as pricing_router
from api_gateway.routes.matrix_routes import router as matrix_router
from api_gateway.routes.config_routes import router as config_router
from api_gateway.routes.admin_pricing_dashboard import router as admin_router

from api_gateway.middleware.logging_middleware import LoggingMiddleware

app = FastAPI(
    title="GenXBaby Pricing Engine Gateway",
    version="1.0.0"
)

# AUTHORIZED FRONTEND DOMAINS
origins = [
    "https://genxbaby-admin-frontend.vercel.app",
    "https://genxbaby-admin-frontend-1qld-eei80eamx-millionmike3s-projects.vercel.app",
    "https://genxbaby-admin-frontend-1qld-bqmcqdmtv-millionmike3s-projects.vercel.app",
    "https://millionmike3s-projects.vercel.app",
    "http://localhost:3000"
]

# LOGGING MIDDLEWARE
app.add_middleware(LoggingMiddleware)

# CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin"
    ],
    max_age=600
)

# API ROUTERS
app.include_router(pricing_router, prefix="/pricing")
app.include_router(matrix_router, prefix="/matrix")
app.include_router(config_router, prefix="/config")
app.include_router(admin_router, prefix="/admin")


# HEALTH CHECK
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "GenXBaby Pricing Engine Gateway"
    }


# ROOT ENDPOINT
@app.get("/")
async def root():
    return {
        "message": "GenXBaby Pricing Engine Gateway is running",
        "status": "online"
    }
