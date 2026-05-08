from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_file": ".env"}

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    ORDER_SERVICE_URL: str = "http://localhost:8000"


settings = Settings()
