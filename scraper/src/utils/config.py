utf-8
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    DATABASE_URL: str
    COSINE_THRESHOLD: float = 0.25
    MIN_CLUSTER_SIZE: int = 2
    LOG_LEVEL: str = "INFO"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
settings = Settings()  