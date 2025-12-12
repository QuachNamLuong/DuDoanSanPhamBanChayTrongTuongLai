# features/predict/controller.py

from .schemas import PredictRequest, PredictResponse, Predict
from .service import predict_next_month


def handle_prediction(req: PredictRequest) -> PredictResponse:
    results = predict_next_month()


    return PredictResponse()
