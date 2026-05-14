from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import AsyncSessionLocal
from src.models.user import Users
from src.repository.user import user_repo
from src.services.auth import verify_token

security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Users:
    payload = verify_token(credentials.credentials, token_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: AsyncSession = Depends(get_db),
) -> Optional[Users]:
    if not credentials:
        return None
    try:
        payload = verify_token(credentials.credentials, token_type="access")
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await user_repo.get(db, user_id)
    except HTTPException:
        return None


def require_role(*roles: str):
    """Dependency factory that enforces role-based access."""

    async def check(current_user: Users = Depends(get_current_user)) -> Users:
        role_name = current_user.role.role if current_user.role else ""
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {roles}. Your role: {role_name}",
            )
        return current_user

    return check


# ── App-state service accessors ───────────────────────────────────────────────

def get_redis(request: Request):
    return request.app.state.redis


def get_sms_service(request: Request):
    return request.app.state.sms_service


def get_otp_service(request: Request):
    return request.app.state.otp_service


def get_google_auth_service(request: Request):
    return request.app.state.google_auth
