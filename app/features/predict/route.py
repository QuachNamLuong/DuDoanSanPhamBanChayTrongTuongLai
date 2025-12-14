from fastapi import APIRouter
from .service import predict_next_quarter

router = APIRouter()

@router.get("/predict", tags=["Predict"])
def predict():
    return predict_next_quarter()
