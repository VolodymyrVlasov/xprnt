import logging
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.dependencies import get_db, get_current_user, get_google_auth_service, get_otp_service, get_sms_service
from src.models.reference import Roles
from src.models.user import Users
from src.repository.company import company_repo
from src.repository.user import user_repo
from src.schemas.auth import (
    GoogleAuthUrlResponse,
    GoogleCallbackResponse,
    LoginRequest,
    RegisterRequest,
    SMSSendCodeRequest,
    SMSVerifyRequest,
    SMSVerifyResponse,
    TokenResponse,
)
from src.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from src.utils.phone import normalize_phone

logger = logging.getLogger(__name__)

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


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await user_repo.get_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

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

    await company_repo.update(db, company, {"contact_user_id": user.id})

    token_data = {"sub": str(user.id), "role": role.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    _set_refresh_cookie(response, refresh_token)
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
    _set_refresh_cookie(response, refresh_token)
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
    _set_refresh_cookie(response, new_refresh)
    return TokenResponse(access_token=new_access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    response.delete_cookie(_REFRESH_COOKIE)


# ── SMS OTP ───────────────────────────────────────────────────────────────────

@router.post("/sms/send-code")
async def sms_send_code(
    data: SMSSendCodeRequest,
    request: Request,
):
    phone = normalize_phone(data.phone)
    otp_service = get_otp_service(request)
    sms_service = get_sms_service(request)

    code = await otp_service.generate_and_store(phone)
    sent = await sms_service.send_otp(phone, code)
    if not sent:
        logger.warning("SMS delivery failed for %s (OTP still stored)", phone)

    result: dict = {"message": "Code sent", "expires_in": settings.OTP_EXPIRE_MINUTES * 60}
    if settings.ENV == "dev":
        result["dev_code"] = code
    return result


@router.post("/sms/verify", response_model=SMSVerifyResponse)
async def sms_verify(
    data: SMSVerifyRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    phone = normalize_phone(data.phone)
    otp_service = get_otp_service(request)

    valid = await otp_service.verify(phone, data.code)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")

    user = await user_repo.get_by_phone(db, phone)
    is_new_user = False

    if not user:
        if not data.name or not data.lastname:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New user registration required: provide name and lastname",
            )
        role = await _get_or_create_default_role(db)
        company_name = f"{data.name} {data.lastname}".strip()
        edrpou = phone.replace("+", "")[-8:]
        company = await company_repo.create(db, {"name": company_name, "edrpou_code": edrpou})
        user = await user_repo.create(
            db,
            {
                "phone1": phone,
                "name": data.name,
                "lastname": data.lastname,
                "email": f"sms.{phone.replace('+', '')}@xprnt.local",
                "auth_provider": "sms",
                "phone_verified": True,
                "role_id": role.id,
                "company_id": company.id,
            },
        )
        await company_repo.update(db, company, {"contact_user_id": user.id})
        is_new_user = True
    else:
        await user_repo.update(db, user, {"phone_verified": True})

    role_name = user.role.role if user.role else ""
    token_data = {"sub": str(user.id), "role": role_name}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    _set_refresh_cookie(response, refresh_token)
    return SMSVerifyResponse(access_token=access_token, is_new_user=is_new_user)


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google", response_model=GoogleAuthUrlResponse)
async def google_auth_init(request: Request):
    state = secrets.token_urlsafe(32)
    redis = request.app.state.redis
    await redis.set(f"oauth_state:{state}", "1", ex=600)

    google_auth = get_google_auth_service(request)
    auth_url = google_auth.get_auth_url(state)
    return GoogleAuthUrlResponse(auth_url=auth_url)


@router.get("/google/callback", response_model=GoogleCallbackResponse)
async def google_auth_callback(
    code: str,
    state: str,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    redis = request.app.state.redis
    state_key = f"oauth_state:{state}"
    valid = await redis.get(state_key)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired state")
    await redis.delete(state_key)

    google_auth = get_google_auth_service(request)
    try:
        tokens = await google_auth.exchange_code(code)
        user_info = await google_auth.get_user_info(tokens["access_token"])
    except Exception as exc:
        logger.error("Google OAuth error: %s", exc)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google auth failed")

    google_id: str = user_info["sub"]
    email: str = user_info.get("email", "")
    given_name: str = user_info.get("given_name", "")
    family_name: str = user_info.get("family_name", "")

    user = await user_repo.get_by_google_id(db, google_id)
    is_new_user = False

    if not user and email:
        user = await user_repo.get_by_email(db, email)
        if user:
            # Link Google account to existing email-registered user
            await user_repo.update(db, user, {"google_id": google_id})

    if not user:
        role = await _get_or_create_default_role(db)
        company_name = f"{given_name} {family_name}".strip() or email
        edrpou = google_id[-8:] if len(google_id) >= 8 else secrets.token_hex(4)
        company = await company_repo.create(db, {"name": company_name, "edrpou_code": edrpou})
        user = await user_repo.create(
            db,
            {
                "email": email or f"google.{google_id}@xprnt.local",
                "name": given_name or "Google",
                "lastname": family_name or "User",
                "google_id": google_id,
                "auth_provider": "google",
                "phone_verified": False,
                "role_id": role.id,
                "company_id": company.id,
            },
        )
        await company_repo.update(db, company, {"contact_user_id": user.id})
        is_new_user = True

    role_name = user.role.role if user.role else ""
    token_data = {"sub": str(user.id), "role": role_name}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    _set_refresh_cookie(response, refresh_token)
    return GoogleCallbackResponse(access_token=access_token, is_new_user=is_new_user)
