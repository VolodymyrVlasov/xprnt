"""Shared pytest fixtures for design-service tests.

MinIO and Redis are mocked so tests run without real infrastructure.
The FastAPI lifespan is patched at the app.main import level so
MinIOClient() and aioredis.from_url() never attempt real connections.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.dependencies import get_current_user, get_db, get_minio, get_redis
from app.main import app


@pytest_asyncio.fixture
async def async_client():
    """
    Yields (client, mock_minio, mock_redis).

    Dependency overrides:
      - get_db        → yields a MagicMock session (repo methods are patched per-test)
      - get_minio     → returns mock_minio
      - get_redis     → returns mock_redis
      - get_current_user → returns a fake user payload (no Bearer token needed)
    """
    mock_minio = MagicMock()
    mock_minio.ensure_buckets = MagicMock()
    mock_minio.upload_file = AsyncMock(return_value="object_name")
    mock_minio.get_file_url = AsyncMock(return_value="http://minio/bucket/file.jpg")
    mock_minio.delete_file = AsyncMock()

    mock_redis = AsyncMock()
    mock_redis.lpush = AsyncMock(return_value=1)
    mock_redis.aclose = AsyncMock()

    async def override_get_db():
        yield MagicMock()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_minio] = lambda: mock_minio
    app.dependency_overrides[get_redis] = lambda: mock_redis
    app.dependency_overrides[get_current_user] = lambda: {"sub": "test-user", "role": "client"}

    with (
        patch("app.main.MinIOClient", return_value=mock_minio),
        patch("app.main.aioredis") as mock_aioredis_module,
    ):
        mock_aioredis_module.from_url.return_value = mock_redis

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac, mock_minio, mock_redis

    app.dependency_overrides.clear()
