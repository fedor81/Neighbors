"""FileStoragePort -> S3/MinIO (boto3). Загрузка фото через бэкенд (решение по открытому вопросу №2)."""
import mimetypes
import uuid

import boto3

from app.core.config import settings
from app.domain.ports.repositories import FileStoragePort

MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 МБ
ALLOWED_MIME_PREFIX = "image/"


class S3FileStorage(FileStoragePort):
    def __init__(self):
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        self._bucket = settings.S3_BUCKET

    @staticmethod
    def validate(data: bytes, content_type: str) -> None:
        if len(data) > MAX_PHOTO_BYTES:
            raise ValueError("Файл превышает 5 МБ")
        mime = content_type or mimetypes.guess_type("x.jpg")[0]
        if not (mime or "").startswith(ALLOWED_MIME_PREFIX):
            raise ValueError("Разрешены только изображения")

    def upload(self, key: str, data: bytes, content_type: str) -> str:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data,
                                ContentType=content_type)
        return f"{settings.S3_ENDPOINT}/{self._bucket}/{key}"

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)


def make_photo_key(item_id: int, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return f"items/{item_id}/{uuid.uuid4().hex}.{ext}"
