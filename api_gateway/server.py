from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ROUTERS — ONLY import the correct matrix router
from api_gateway.routes.pricing_routes import router as pricing_router
from api_gateway.routes.matrix_routes import router as matrix_router
from api_gateway.routes.config_routes import router as config_router
from api_gateway.routes.admin_pricing_dashboard import router as admin_router

from api_gateway.middleware.logging_middleware import LoggingMiddleware

app = FastAPI(
    title="GenXBaby Pricing Engine Gateway",
    version="1.0.0"
)

# CORS — allow all Vercel admin frontend domains
origins = [
    "https://genxbaby-admin-frontend.vercel.app",
    "https://genxbaby-admin-frontend-1qld-eei80eamx-millionmike3s-projects.vercel.app",
    "https://genxbaby-admin-frontend-1qld-bqmcqdmtv-millionmike3s-projects.vercel.app",
    "https://millionmike3s-projects.vercel.app",
    "http://localhost:3000"
]

# ⭐ MIDDLEWARE MUST COME FIRST
app.add_middleware(LoggingMiddleware)

# ⭐ CORS MUST COME AFTER LOGGING
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⭐ ROUTES MUST COME LAST
app.include_router(pricing_router, prefix="/pricing")
app.include_router(matrix_router, prefix="/matrix")
app.include_router(config_router, prefix="/config")
app.include_router(admin_router, prefix="/admin")

if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(
        "api_gateway.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=False
    )
