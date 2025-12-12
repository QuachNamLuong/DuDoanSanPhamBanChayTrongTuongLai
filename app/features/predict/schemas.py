from pydantic import BaseModel

class Predict(BaseModel):
    variant_id: int
    order_quantity_next_month: float | int 

class PredictRequest(BaseModel):
    variant_ids: list[int] | None = None

class PredictResponse(BaseModel):
    predicts: list[Predict]
