from datetime import datetime, timedelta
from jose import jwt
import httpx

from app.core.config import settings


def create_access_token(data: dict) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def verify_google_token(id_token: str) -> dict | None:
    """Google ID 토큰 검증"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
            )
            if response.status_code == 200:
                data = response.json()
                # Client ID 검증
                if data.get("aud") == settings.GOOGLE_CLIENT_ID:
                    return data
            return None
    except Exception:
        return None
