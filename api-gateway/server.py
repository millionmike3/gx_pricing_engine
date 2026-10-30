# backend/api-gateway/server.py
from fastapi import FastAPI
from routes.pricing_routes import router as pricing_router
from routes.matrix_routes import router as matrix_router
from routes.config_routes import router as config_router
from middleware.logging_middleware import LoggingMiddleware
from middleware.auth_middleware import AuthMiddleware

app = FastAPI(
    title="GenXBaby Pricing Engine Gateway",
    version="1.0.0"
)

app.include_router(pricing_router, prefix="/pricing")
app.include_router(matrix_router, prefix="/matrix")
app.include_router(config_router, prefix="/config")
app.add_middleware(LoggingMiddleware)
