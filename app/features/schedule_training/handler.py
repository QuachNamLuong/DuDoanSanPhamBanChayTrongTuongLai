from app.features.schedule_training.repo import get_historical_data, save_trained_model
from app.features.schedule_training.train import train_model


async def train_model_handler():
    print("[JOB] Quarterly training job started")

    data = await get_historical_data()
    model = train_model(data)
    await save_trained_model(model)

    print("[JOB] Training job completed successfully")
