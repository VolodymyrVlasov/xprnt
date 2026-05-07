from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DB
    DESIGN_DB_URL: str = "postgresql+asyncpg://postgres:postgres@postgres-design:5432/design_db"

    # JWT (shared with order-service)
    JWT_SECRET: str = "change_me_in_production"
    JWT_ALGORITHM: str = "HS256"

    # MinIO
    MINIO_ENDPOINT: str = "minio:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    class Config:
        env_file = ".env"


settings = Settings()
