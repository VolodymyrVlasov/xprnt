import asyncio
import io
import uuid
from datetime import timedelta
from functools import partial
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.config import settings

BUCKET_UPLOADS = "uploads"
BUCKET_PREVIEWS = "previews"


class MinIOClient:
    def __init__(self) -> None:
        self._client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def _ensure_bucket(self, bucket: str) -> None:
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    def ensure_buckets(self) -> None:
        """Create required buckets if they don't exist. Call at startup."""
        for bucket in (BUCKET_UPLOADS, BUCKET_PREVIEWS):
            self._ensure_bucket(bucket)

    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        file_data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        loop = asyncio.get_event_loop()
        data = io.BytesIO(file_data)
        await loop.run_in_executor(
            None,
            partial(
                self._client.put_object,
                bucket,
                object_name,
                data,
                len(file_data),
                content_type,
            ),
        )
        return object_name

    async def get_file_url(self, bucket: str, object_name: str) -> str:
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            None,
            partial(
                self._client.presigned_get_object,
                bucket,
                object_name,
                expires=timedelta(days=7),
            ),
        )
        return url

    async def delete_file(self, bucket: str, object_name: str) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            partial(self._client.remove_object, bucket, object_name),
        )

    @staticmethod
    def generate_object_name(filename: str, prefix: str = "") -> str:
        unique = uuid.uuid4().hex
        safe_name = filename.replace(" ", "_")
        if prefix:
            return f"{prefix}/{unique}_{safe_name}"
        return f"{unique}_{safe_name}"
