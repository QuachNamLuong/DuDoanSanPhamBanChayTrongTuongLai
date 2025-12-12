# features/predict/router.py
from fastapi import APIRouter
from .schemas import PredictRequest, PredictResponse
from .controller import handle_prediction

router = APIRouter(prefix="/predict", tags=["prediction"])

@router.get("/", response_model=PredictResponse)
def predict_orders(payload: PredictRequest):
    return handle_prediction(payload)
