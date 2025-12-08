from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""

    # 基本設定
    ENV: str = "local"
    DEBUG: bool = True
    APP_NAME: str = "Learning Platform API"
    APP_VERSION: str = "0.1.0"

    # CORS設定
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # AWS設定
    AWS_REGION: str = "ap-northeast-1"
    DYNAMODB_ENDPOINT: str = ""

    # 認証設定
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Slack設定
    SLACK_CLIENT_ID: str = ""
    SLACK_CLIENT_SECRET: str = ""
    SLACK_SIGNING_SECRET: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()