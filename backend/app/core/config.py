from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Core
    DATABASE_URL: str = "sqlite+aiosqlite:///./plagiarism_detection.db"
    SECRET_KEY: str = "super-secret-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DEBUG: bool = True  # ✅ Added (required by db.py)

    # Redis / Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # S3 Storage
    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = ""

    # AI Integrations
    OPENAI_API_KEY: Optional[str] = ""
    ZEROGPT_API_KEY: Optional[str] = ""
    COPYLEAKS_API_KEY: Optional[str] = ""
    USE_EXTERNAL_AI_DETECTION: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
