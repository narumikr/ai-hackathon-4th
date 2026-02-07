"""ストレージサービスファクトリー"""

from app.application.ports.storage_service import IStorageService
from app.config.settings import Settings
from app.infrastructure.storage.cloud_storage import CloudStorageService
from app.infrastructure.storage.local_storage import LocalStorageService


def create_storage_service(settings: Settings) -> IStorageService:
    """設定に基づいてストレージサービスを作成する

    Args:
        settings: アプリケーション設定

    Returns:
        IStorageService: ストレージサービス実装

    Raises:
        ValueError: サポートされていないストレージタイプ
    """
    storage_type = settings.storage_type.lower()

    if storage_type == "local":
        # ローカル開発用ストレージ
        return LocalStorageService(
            upload_dir=settings.upload_dir,
        )
    elif storage_type == "gcs":
        # Google Cloud Storage
        if not settings.gcs_bucket_name:
            raise ValueError("GCS_BUCKET_NAMEが設定されていません。")

        return CloudStorageService(
            bucket_name=settings.gcs_bucket_name,
            project_id=settings.google_cloud_project,
            signing_service_account_email=settings.cloud_tasks_service_account_email,
        )
    else:
        raise ValueError(
            f"サポートされていないストレージタイプです: {storage_type}。対応タイプ: local, gcs"
        )
