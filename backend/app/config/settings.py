"""アプリケーション設定."""

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import field_validator, model_validator
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
    database_url: str = ""
    database_host: str | None = None
    database_name: str | None = None
    database_user: str | None = None
    database_password: str | None = None
    debug: bool = False

    @model_validator(mode="after")
    def build_database_url(self) -> "DatabaseSettings":
        """DATABASE_URLが未設定の場合、個別の環境変数から構築."""
        if self.database_url:
            return self

        # 個別の環境変数からDATABASE_URLを構築
        if all(
            [self.database_host, self.database_name, self.database_user, self.database_password]
        ):
            assert self.database_user is not None
            assert self.database_password is not None
            assert self.database_name is not None
            user = quote_plus(self.database_user)
            password = quote_plus(self.database_password)
            database_name = quote_plus(self.database_name)
            self.database_url = (
                f"postgresql://{user}:{password}@{self.database_host}/{database_name}"
            )
            return self

        raise ValueError(
            "DATABASE_URLまたは(DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD)が必要です"
        )


class Settings(DatabaseSettings):
    """アプリケーション設定（FastAPI用の全設定）."""

    # アプリケーション設定
    app_name: str = "Historical Travel Agent"

    # CORS設定
    cors_origins: list[str] = ["http://localhost:3000"]

    # Redis設定
    redis_url: str = "redis://localhost:6379"  # デフォルト値を設定

    # Google Cloud設定
    google_cloud_project: str | None = None
    google_cloud_location: str = "asia-northeast1"
    google_application_credentials: str | None = None  # ADC使用時は不要

    # ストレージ設定
    storage_type: Literal["local", "gcs"] = "local"
    upload_dir: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    gcs_bucket_name: str | None = None  # GCSバケット名（本番環境用）

    # Gemini設定
    gemini_model_name: str = "gemini-2.5-flash"
    gemini_temperature: float = 0.7
    gemini_max_output_tokens: int = 8192
    gemini_timeout_seconds: int = 60
    # TODO: 将来の拡張用 - thinking_levelパラメータの活用
    gemini_thinking_level: str = "medium"  # minimal, low, medium, high（未実装）

    # 画像生成設定
    image_generation_model: str = "gemini-2.5-flash-image"
    image_generation_location: str = "global"
    image_generation_max_concurrent: int = 1
    image_generation_job_lock_timeout_seconds: int = 900
    image_generation_aspect_ratio: str = "16:9"
    image_generation_timeout: int = 60

    # ログ設定
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_force_override: bool = False  # 既存のロガー設定を強制上書きするか

    def get_effective_log_level(self) -> str:
        """debugフラグに基づいて有効なログレベルを取得

        Requirements:
        - 4.2: debug=True の場合は DEBUG レベル
        - 4.3: debug=False の場合は INFO レベル以上
        """
        if self.debug:
            return "DEBUG"
        return self.log_level

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """ログレベルの妥当性を検証"""
        normalized = value.strip().upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in valid_levels:
            raise ValueError(f"log_levelが不正です: {value}")
        return normalized

    @field_validator("google_cloud_project")
    @classmethod
    def validate_google_cloud_project(cls, value: str | None) -> str | None:
        """Google Cloud Projectの検証（GCS使用時のみ必須）"""
        # GCS使用時はチェックするが、ここでは緩く設定
        return value

    @field_validator("image_generation_job_lock_timeout_seconds")
    @classmethod
    def validate_image_generation_job_lock_timeout_seconds(cls, value: int) -> int:
        """ジョブロックのタイムアウト秒数を検証する"""
        if value <= 0:
            raise ValueError("image_generation_job_lock_timeout_seconds must be positive.")
        return value

    @field_validator("google_application_credentials")
    @classmethod
    def validate_credentials_path(cls, value: str | None) -> str | None:
        """認証情報ファイルの存在チェック（設定されている場合のみ）"""
        if value is None or not value.strip():
            # ADC (Application Default Credentials) を使用
            return None
        if not Path(value).exists():
            raise ValueError(f"GOOGLE_APPLICATION_CREDENTIALS が存在しません: {value}")
        return value


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """データベース設定のみ取得（Alembic、テスト用）"""
    return DatabaseSettings()  # type: ignore[call-arg]


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンインスタンスを取得"""
    return Settings()  # type: ignore[call-arg]
