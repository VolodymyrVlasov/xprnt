from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.dev", extra="ignore")

    ENV: str = "dev"
    ORDER_DB_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/order_db"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30


settings = Settings()
