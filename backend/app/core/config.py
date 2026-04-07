from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "TerraLedger"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    DATABASE_URL: str = "postgresql://terraledger:terraledger@localhost:5432/terraledger_db"

    SATELLITE_MODE: str = "demo"  # "demo" or "live"
    GEE_SERVICE_ACCOUNT: str = ""
    GEE_KEY_FILE: str = ""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    DEMO_EMAIL: str = "demo@terraledger.io"
    DEMO_PASSWORD: str = "TerraDemo2026"

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
