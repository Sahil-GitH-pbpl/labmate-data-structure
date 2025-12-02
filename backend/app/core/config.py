from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field, AnyHttpUrl


class Settings(BaseSettings):
    app_name: str = "Hiccup System"
    app_version: str = "1.0.0"
    app_env: str = Field("dev", env="APP_ENV")
    api_prefix: str = "/api"

    db_host: str = Field("mysql", env="DB_HOST")
    db_port: int = Field(3306, env="DB_PORT")
    db_user: str = Field("hiccup_user", env="DB_USER")
    db_password: str = Field("hiccup_pass", env="DB_PASSWORD")
    db_name: str = Field("hiccup_db", env="DB_NAME")
    database_url: Optional[str] = Field(None, env="DATABASE_URL")

    jwt_secret: str = Field("supersecret", env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGO")
    jwt_issuer: str = Field("arpra", env="JWT_ISSUER")
    jwt_audience: str = Field("arpra", env="JWT_AUDIENCE")

    whatsapp_api_url: str = Field("https://api.stewindia.test/send", env="WHATSAPP_API_URL")
    whatsapp_api_token: str = Field("changeme", env="WHATSAPP_API_TOKEN")
    management_group_numbers: List[str] = Field("", env="MANAGEMENT_GROUP_NUMBERS")

    upload_dir: str = Field("uploads/hiccups", env="UPLOAD_DIR")
    logs_dir: str = Field("logs", env="LOGS_DIR")

    timezone: str = Field("Asia/Kolkata", env="TIMEZONE")
    cors_origins: List[AnyHttpUrl] | List[str] = Field(
        default_factory=lambda: ["http://localhost:7411", "http://localhost:3000"],
        env="CORS_ORIGINS",
    )
    internal_token: str = Field("internal-token", env="INTERNAL_TOKEN")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/"
            f"{self.db_name}"
        )

    @property
    def management_numbers(self) -> List[str]:
        numbers: List[str] = []
        if isinstance(self.management_group_numbers, list):
            for value in self.management_group_numbers:
                numbers.extend([v.strip() for v in value.split(",") if v.strip()])
        elif isinstance(self.management_group_numbers, str):
            numbers = [v.strip() for v in self.management_group_numbers.split(",") if v.strip()]
        return numbers


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
