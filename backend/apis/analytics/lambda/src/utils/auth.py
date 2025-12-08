from typing import Optional
import jwt
import json
from datetime import datetime

from utils.config import settings


class AuthError(Exception):
    """認証エラー"""
    pass


def extract_user_id_from_token(token: str) -> str:
    """JWTトークンからユーザーIDを抽出"""
    
    try:
        # 開発環境では簡単なトークン検証
        if settings.ENV == "local":
            # テスト用のトークン処理
            if token == "test-token":
                return "test-user-1"
            elif token.startswith("user-"):
                return token
            else:
                return "test-user-1"  # デフォルトのテストユーザー
        
        # 本番環境ではJWT検証
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            user_id = payload.get("user_id")
            if not user_id:
                raise AuthError("トークンにuser_idが含まれていません")
            
            # トークンの有効期限チェック
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                raise AuthError("トークンの有効期限が切れています")
            
            return user_id
            
        except jwt.InvalidTokenError as e:
            raise AuthError(f"無効なトークンです: {str(e)}")
    
    except AuthError:
        raise
    except Exception as e:
        raise AuthError(f"トークン処理エラー: {str(e)}")


def extract_user_id_from_event(event: dict) -> str:
    """Lambda イベントからユーザーIDを抽出"""
    
    try:
        # API Gateway経由の場合
        headers = event.get("headers", {})
        
        # Authorizationヘッダーをチェック
        auth_header = headers.get("Authorization") or headers.get("authorization")
        if auth_header:
            # "Bearer <token>" 形式
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # "Bearer " を除去
                return extract_user_id_from_token(token)
        
        # クエリパラメータからトークンを取得（開発用）
        query_params = event.get("queryStringParameters") or {}
        token = query_params.get("token")
        if token:
            return extract_user_id_from_token(token)
        
        # パスパラメータからユーザーIDを取得
        path_params = event.get("pathParameters") or {}
        user_id = path_params.get("user_id")
        if user_id:
            return user_id
        
        # デフォルト（開発環境のみ）
        if settings.ENV == "local":
            return "test-user-1"
        
        raise AuthError("認証情報が見つかりません")
        
    except AuthError:
        raise
    except Exception as e:
        raise AuthError(f"認証処理エラー: {str(e)}")


def validate_user_access(user_id: str, resource_user_id: Optional[str] = None) -> bool:
    """ユーザーのリソースアクセス権を検証"""
    
    try:
        # リソースが特定のユーザーに紐づく場合のチェック
        if resource_user_id and user_id != resource_user_id:
            return False
        
        # 基本的なユーザーID検証
        if not user_id or len(user_id.strip()) == 0:
            return False
        
        # 管理者権限やその他の権限チェックをここに追加
        # 現在は基本的なチェックのみ
        
        return True
        
    except Exception:
        return False


def create_auth_response(status_code: int, message: str, details: Optional[dict] = None) -> dict:
    """認証エラーレスポンスを作成"""
    
    response_body = {
        "error": "AuthError",
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        response_body["details"] = details
    
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(response_body)
    }