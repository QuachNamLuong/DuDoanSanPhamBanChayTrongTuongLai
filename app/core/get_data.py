import os
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    # =========================
    # App Settings
    # =========================
    APP_NAME: str = "FastAPI Vertical Slice App"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # =========================
    # CORS Settings
    # =========================
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # =========================
    # Database Settings
    # =========================
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "mydb"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # =========================
    # ML Model Settings
    # =========================
    MODEL_DIR: str = "models"
    MODEL_FILENAME: str = "xgb_order_predictor.json"

    @property
    def MODEL_PATH(self) -> str:
        return os.path.join(self.MODEL_DIR, self.MODEL_FILENAME)

    # =========================
    # Scheduler Settings
    # =========================
    ENABLE_SCHEDULER: bool = True
    RETRAIN_CRON: str = "0 0 1 * *"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings():
    return Settings()
