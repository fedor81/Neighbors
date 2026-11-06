"""S3/MinIO client (заглушка интерфейса). Загрузка фото через бэкенд."""
import boto3

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
    )


def upload_item_photo(item_id: int, data: bytes, filename: str) -> str:
    """TODO: валидация MIME/размера (<5МБ), сжатие, key=items/{item_id}/{uuid}.jpg -> URL."""
    raise NotImplementedError
