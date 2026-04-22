from minio import Minio
from minio.error import S3Error
from app.config import settings

_client: Minio | None = None


def get_storage() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_root_user,
            secret_key=settings.minio_root_password,
            secure=settings.minio_secure,
        )
    return _client


def ensure_bucket() -> None:
    client = get_storage()
    bucket = settings.minio_bucket_name
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    except S3Error as exc:
        raise RuntimeError(f"Could not ensure MinIO bucket: {exc}") from exc
