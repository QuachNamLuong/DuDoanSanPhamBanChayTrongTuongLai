from fastapi import FastAPI
from app.api.health import router as health_router
from app.features.predict.route import router as predict_router

app = FastAPI(title="My API")

# Register routes
app.include_router(health_router, prefix="/api")
