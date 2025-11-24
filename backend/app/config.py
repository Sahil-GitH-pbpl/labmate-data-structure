import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")


class Settings:
    database_url_env: str = os.getenv("DATABASE_URL", "")
    app_env: str = os.getenv("APP_ENV", "dev")
    app_port: int = int(os.getenv("APP_PORT", 8000))

    db_host: str = os.getenv("DB_HOST", "mysql")
    db_port: int = int(os.getenv("DB_PORT", 3306))
    db_user: str = os.getenv("DB_USER", "infra_user")
    db_pass: str = os.getenv("DB_PASS", "infra_pass")
    db_name: str = os.getenv("DB_NAME", "infra_db")

    admin_emails: List[str] = [email.strip() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()]
    timezone: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads/infra")
    max_image_mb: int = int(os.getenv("MAX_IMAGE_MB", 5))
    jwt_audience: str = os.getenv("JWT_AUDIENCE", "arpra")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "arpra")
    cors_origins: List[str] = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8000,http://localhost:3000").split(",")
    ]

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url_env:
            return self.database_url_env
        return f"mysql+pymysql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
