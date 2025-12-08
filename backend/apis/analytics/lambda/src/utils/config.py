import os
from typing import List
from pydantic_settings import BaseSettings


class AnalyticsSettings(BaseSettings):
    """Analytics サービスの設定"""

    # 基本設定
    ENV: str = os.getenv("ENV", "local")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    SERVICE_NAME: str = "analytics"
    SERVICE_VERSION: str = "0.1.0"

    # CORS設定
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # AWS設定
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-1")
    DYNAMODB_ENDPOINT: str = os.getenv("DYNAMODB_ENDPOINT", "")

    # DynamoDBテーブル名
    USERS_TABLE: str = os.getenv("USERS_TABLE", "Users")
    TIMER_TABLE: str = os.getenv("TIMER_TABLE", "Timer")
    RECORDS_TABLE: str = os.getenv("RECORDS_TABLE", "Records")
    ROADMAP_TABLE: str = os.getenv("ROADMAP_TABLE", "Roadmap")

    # キャッシュ設定
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))

    # 分析設定
    MAX_ANALYSIS_PERIOD_DAYS: int = int(os.getenv("MAX_ANALYSIS_PERIOD_DAYS", "365"))
    DEFAULT_ANALYSIS_PERIOD_DAYS: int = int(os.getenv("DEFAULT_ANALYSIS_PERIOD_DAYS", "30"))

    # 認証設定
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # ログ設定
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AnalyticsSettings()