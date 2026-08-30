import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra = "ignore")
    PROJECT_NAME: str = "SIH26103 - Integrated Project Monitoring Platform"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = Field(validation_alias="JWT_SECRET_KEY")
    ALGORITHM: str = Field(validation_alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    # Email & OTP Settings
    EMAIL_HOST: str = Field(default="smtp.gmail.com")
    EMAIL_PORT: int = Field(default=587)
    EMAIL_USERNAME: str = Field(default="")
    EMAIL_PASSWORD: str = Field(default="")
    OTP_EXPIRE_MINUTES: int = Field(default=2)
    OTP_MAX_ATTEMPTS: int = Field(default=5)
    OTP_RESEND_COOLDOWN_SECONDS: int = Field(default=60)

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sih_project_monitoring.db")

    # Machine Learning Model Path
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", "ml/saved_model/model_bundle.joblib")

settings = Settings()

