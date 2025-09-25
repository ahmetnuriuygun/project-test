from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    UNKNOWN_RFID_RETENTION_DAYS: int = 30  # Default to 30 days

    class Config:
        env_file = ".env"

settings = Settings()
