import os
from fastapi import FastAPI
from app.api.health import router as health_router
from app.features.predict.route import router as predict_router
from app.features.schedule_training.handler import train_model_handler
from app.features.schedule_training.scheduler import start_scheduler
from app.logging import setup_logging

app = FastAPI(title="My API")

# Register routes
# app.include_router(health_router, prefix="/api")
app.include_router(predict_router, prefix="/api")

@app.on_event("startup")
def startup():
    setup_logging()

@app.on_event("startup")
def startup_event():
    # if os.environ.get("RUN_MAIN") == "true":
        start_scheduler()

