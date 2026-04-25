from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import get_db, get_current_user
from src.models.reference import Roles
from src.models.user import Users
from src.repository.company import company_repo
from src.repository.user import user_repo
from src.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from src.schemas.user import UserResponse
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_DEFAULT_ROLE = "client"
_REFRESH_COOKIE = "refresh_token"


async def _get_or_create_default_role(db: AsyncSession) -> Roles:
    result = await db.execute(select(Roles).where(Roles.role == _DEFAULT_ROLE))
    role = result.scalar_one_or_none()
    if not role:
        role = Roles(role=_DEFAULT_ROLE)
        db.add(role)
        await db.commit()
        await db.refresh(role)
    return role


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await user_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Create company first (contact_user_id will be set after user creation)
    company_name = data.company_name or f"{data.name} {data.lastname}".strip()
    company = await company_repo.get_by_edrpou(db, data.company_edrpou)
    if not company:
        company = await company_repo.create(
            db, {"edrpou_code": data.company_edrpou, "name": company_name}
        )

    role = await _get_or_create_default_role(db)

    user = await user_repo.create(
        db,
        {
            "email": data.email,
            "hashed_password": hash_password(data.password),
            "name": data.name,
            "lastname": data.lastname,
            "phone1": data.phone1,
            "company_id": company.id,
            "role_id": role.id,
        },
    )

    # Set company contact user
    await company_repo.update(db, company, {"contact_user_id": user.id})

    token_data = {"sub": str(user.id), "role": role.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await user_repo.get_by_email(db, data.email)
    if not user or not user.hashed_password or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    role_name = user.role.role if user.role else ""
    token_data = {"sub": str(user.id), "role": role_name}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.cookies.get(_REFRESH_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    payload = verify_token(token, token_type="refresh")
    user_id = payload.get("sub")
    user = await user_repo.get(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    role_name = user.role.role if user.role else ""
    token_data = {"sub": str(user.id), "role": role_name}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=new_refresh,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return TokenResponse(access_token=new_access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(_REFRESH_COOKIE)
