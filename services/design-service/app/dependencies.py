from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.utils.file_storage import MinIOClient

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Optional[dict]:
    if not credentials:
        return None
    try:
        return jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


async def get_minio(request: Request) -> MinIOClient:
    return request.app.state.minio


async def get_redis(request: Request) -> Redis:
    return request.app.state.redis
