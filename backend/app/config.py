from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MongoDB
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db_name: str = "drivedb"

    # MinIO
    minio_endpoint: str = "minio:9000"
    minio_root_user: str = "minioadmin"
    minio_root_password: str = "minioadmin"
    minio_bucket_name: str = "drive-files"
    minio_secure: bool = False

    # Backend
    backend_cors_origins: list[str] = ["http://localhost:3000"]
    max_upload_size_bytes: int = 2 * 1024 * 1024 * 1024  # 2 GB

    # Auth / JWT
    jwt_secret: str = "change-me-to-a-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    # Storage quotas
    default_quota_bytes: int = 10 * 1024 * 1024 * 1024  # 10 GB

    model_config = SettingsConfigDict(
        env_file=("../.env", "../.env.local", ".env"),
        extra="ignore",
    )


settings = Settings()
