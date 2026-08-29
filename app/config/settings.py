import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIH26103 - Integrated Project Monitoring Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sih26103_super_secret_jwt_key_2026_change_in_prod")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sih_project_monitoring.db")

    # Machine Learning Model Path
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "ml/saved_model/model_bundle.joblib")

    class Config:
        case_sensitive = True

settings = Settings()
