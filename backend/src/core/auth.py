from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt

from src.core.config import settings

security = HTTPBearer()


def create_access_token(user_id: str, email: str) -> str:
    """JWTアクセストークンを作成"""
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """JWTトークンを検証"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            return None
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """現在のユーザーIDを取得"""
    
    # 開発環境ではトークン検証をスキップ（簡略化のため）
    if settings.ENV == "local":
        # テスト用のユーザーIDを返す
        return "test-user-1"
    
    # 本番環境ではJWT検証を行う
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効なトークンです",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload.get("user_id")


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """オプショナルなユーザー認証（未認証でもアクセス可能）"""
    if credentials is None:
        return None
    
    if settings.ENV == "local":
        return "test-user-1"
    
    payload = verify_token(credentials.credentials)
    if payload is None:
        return None
    
    return payload.get("user_id")