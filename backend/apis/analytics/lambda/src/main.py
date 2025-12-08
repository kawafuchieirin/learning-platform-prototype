from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import os
import sys

# パス設定
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from handlers.analytics_handler import router as analytics_router
from utils.config import settings

app = FastAPI(
    title="Analytics Service",
    description="学習プラットフォーム - Analytics マイクロサービス",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(analytics_router, prefix="/analytics")

# ヘルスチェック
@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "healthy", 
        "service": "analytics",
        "version": "0.1.0"
    }

@app.get("/")
async def root():
    """ルートエンドポイント"""
    return {
        "service": "analytics",
        "message": "Analytics Service for Learning Platform",
        "version": "0.1.0"
    }

# Lambda用のハンドラー
handler = Mangum(app)