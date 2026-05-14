import logging

import httpx

logger = logging.getLogger(__name__)


class TurboSMSService:
    BASE_URL = "https://api.turbosms.ua"

    def __init__(self, api_key: str, sender: str):
        self.api_key = api_key
        self.sender = sender

    async def send_otp(self, phone: str, code: str) -> bool:
        """
        Send OTP via TurboSMS.
        Phone must be in +380XXXXXXXXX format.
        Returns True on success, False on error (never raises).
        """
        message = f"xprnt код: {code}. Дійсний 5 хвилин."
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{self.BASE_URL}/message/send.json",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "recipients": [phone],
                        "sms": {"sender": self.sender, "text": message},
                    },
                )
                resp.raise_for_status()
                return True
        except Exception as exc:
            logger.error("TurboSMS send_otp failed for %s: %s", phone, exc)
            return False

    async def get_balance(self) -> float:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{self.BASE_URL}/user/balance.json",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            resp.raise_for_status()
            return float(resp.json().get("balance", 0))
