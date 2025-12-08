"""
ローカル開発用 FastAPI アプリケーション
Lambda関数のコードをローカル環境でテストするためのWrapper
"""

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uvicorn
import json

# メインのLambda関数をインポート
from main import lambda_handler

# FastAPIアプリケーション初期化
app = FastAPI(
    title="Learning Platform - Records API",
    description="学習記録の管理API（ローカル開発版）",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    """
    ヘルスチェックエンドポイント
    """
    return {
        "status": "healthy",
        "service": "records-api",
        "environment": os.getenv("ENV", "local")
    }

# メインAPIエンドポイント（Lambda関数へのプロキシ）
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy_to_lambda(request: Request, path: str):
    """
    すべてのAPIリクエストをLambda関数にプロキシ
    """
    try:
        # リクエストボディを取得
        body = None
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            if body:
                body = body.decode('utf-8')

        # Lambda関数用のイベントを構築
        event = {
            "httpMethod": request.method,
            "path": f"/{path}",
            "pathParameters": dict(request.path_params) or None,
            "queryStringParameters": dict(request.query_params) or None,
            "headers": dict(request.headers),
            "body": body,
            "requestContext": {
                "authorizer": {
                    "claims": {
                        "sub": "local-user-id-for-testing"  # ローカル開発用のダミーユーザーID
                    }
                }
            }
        }

        # Lambda関数を実行
        context = type('Context', (), {})()  # ダミーのコンテキスト
        
        print(f"DEBUG: Calling lambda_handler with event: {event}")
        response = lambda_handler(event, context)
        print(f"DEBUG: Lambda response: {response}")

        # レスポンスを返す
        status_code = response.get("statusCode", 200)
        body = response.get("body", "")
        headers = response.get("headers", {})

        # FastAPIのレスポンス形式に合わせて変換
        if status_code >= 400:
            raise HTTPException(status_code=status_code, detail=body)

        # JSONレスポンスとして正しく返す
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
                return body_data
            except:
                return {"result": body}
        return body

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MangumでAWS Lambda互換にする（オプション）
handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )