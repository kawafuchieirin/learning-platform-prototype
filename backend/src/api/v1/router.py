from fastapi import APIRouter

# Analytics APIを追加
from src.api.v1.endpoints import analytics

# 各機能のルーターを将来的に追加
# from src.api.v1.endpoints import timer, roadmap, slack, records

api_router = APIRouter()

# 一旦サンプルエンドポイントを追加
@api_router.get("/")
async def root():
    """API ルートエンドポイント"""
    return {"message": "Learning Platform API v1"}


@api_router.get("/status")
async def api_status():
    """API ステータス"""
    return {"status": "ok", "version": "1.0"}


# Analytics APIを統合
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# 将来的に各機能のルーターを追加
# api_router.include_router(timer.router, prefix="/timer", tags=["Timer"])
# api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Roadmap"])
# api_router.include_router(slack.router, prefix="/slack", tags=["Slack"])
# api_router.include_router(records.router, prefix="/records", tags=["Records"])