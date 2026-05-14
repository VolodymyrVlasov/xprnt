import json
import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status

from src.config import settings


class OTPService:
    def __init__(self, redis_client):
        self.redis = redis_client

    def _key(self, phone: str) -> str:
        return f"otp:{phone}"

    async def generate_and_store(self, phone_e164: str) -> str:
        """
        Generate a 6-digit OTP, store in Redis with TTL.
        Raises HTTP 429 if resend cooldown hasn't elapsed.
        Returns the generated code.
        """
        key = self._key(phone_e164)
        existing = await self.redis.get(key)
        if existing:
            data = json.loads(existing)
            created_at = datetime.fromisoformat(data["created_at"])
            elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
            if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
                wait = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Please wait {wait} seconds before requesting a new code",
                )

        code = str(secrets.randbelow(10 ** settings.OTP_CODE_LENGTH)).zfill(settings.OTP_CODE_LENGTH)
        payload = json.dumps({
            "code": code,
            "attempts": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        await self.redis.set(key, payload, ex=settings.OTP_EXPIRE_MINUTES * 60)
        return code

    async def verify(self, phone_e164: str, code: str) -> bool:
        """
        Verify OTP code.
        Raises HTTP 400 if expired/not found.
        Raises HTTP 429 if max attempts exceeded.
        Returns True on match (deletes OTP), False on mismatch.
        """
        key = self._key(phone_e164)
        raw = await self.redis.get(key)
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code expired or not found",
            )

        data = json.loads(raw)
        data["attempts"] += 1

        if data["attempts"] > settings.OTP_MAX_ATTEMPTS:
            await self.redis.delete(key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts",
            )

        if data["code"] == code:
            await self.redis.delete(key)
            return True

        # Persist updated attempts, preserve remaining TTL
        ttl = await self.redis.ttl(key)
        await self.redis.set(key, json.dumps(data), ex=max(ttl, 1))
        return False

    async def delete(self, phone_e164: str) -> None:
        await self.redis.delete(self._key(phone_e164))
