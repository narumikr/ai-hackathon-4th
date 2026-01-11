"""アプリケーション設定."""

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """データベース設定（Alembicやテスト用の最小設定）."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # 余分な環境変数を無視
    )

    # データベース設定
    database_url: str
    debug: bool = False

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str | None) -> str:
        """データベースURLの必須検証."""
        if value is None or not value.strip():
            raise ValueError("DATABASE_URLは必須です。")
        return value


class Settings(DatabaseSettings):
    """アプリケーション設定（FastAPI用の全設定）."""

    # アプリケーション設定
    app_name: str = "Historical Travel Agent"

    # CORS設定
    cors_origins: list[str] = ["http://localhost:3000"]

    # Redis設定
    redis_url: str

    # Google Cloud設定
    google_cloud_project: str
    google_cloud_location: str = "asia-northeast1"
    google_application_credentials: str | None = None  # ADC使用時は不要

    # ストレージ設定
    upload_dir: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB

    @field_validator("redis_url", "google_cloud_project")
    @classmethod
    def validate_required(cls, value: str | None) -> str:
        """必須設定の空文字や未設定（None）を禁止."""
        if value is None or not value.strip():
            raise ValueError("必須設定が未設定です。")
        return value

    @field_validator("google_application_credentials")
    @classmethod
    def validate_credentials_path(cls, value: str | None) -> str | None:
        """認証情報ファイルの存在チェック（設定されている場合のみ）."""
        if value is None or not value.strip():
            # ADC (Application Default Credentials) を使用
            return None
        if not Path(value).exists():
            raise ValueError(f"GOOGLE_APPLICATION_CREDENTIALS が存在しません: {value}")
        return value


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """データベース設定のみ取得（Alembic、テスト用）."""
    return DatabaseSettings()  # type: ignore[call-arg]


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得."""
    return Settings()  # type: ignore[call-arg]
