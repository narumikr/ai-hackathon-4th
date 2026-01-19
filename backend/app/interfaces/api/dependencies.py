"""API依存性注入の定義"""

from functools import lru_cache

from app.application.ports.ai_service import IAIService
from app.application.ports.storage_service import IStorageService
from app.config.settings import Settings, get_settings
from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient
from app.infrastructure.storage.factory import create_storage_service


async def get_settings_dependency() -> Settings:
    """設定のシングルトンインスタンスを取得する依存性

    Returns:
        Settings: アプリケーション設定
    """
    return get_settings()


@lru_cache(maxsize=1)
def get_storage_service() -> IStorageService:
    """ストレージサービスのシングルトンインスタンスを取得する

    Returns:
        IStorageService: ストレージサービス実装
    """
    settings = get_settings()
    return create_storage_service(settings)


async def get_storage_service_dependency() -> IStorageService:
    """ストレージサービスの依存性

    Returns:
        IStorageService: ストレージサービス
    """
    return get_storage_service()


@lru_cache(maxsize=1)
def get_ai_service() -> IAIService:
    """AIサービスのシングルトンインスタンスを取得する

    Returns:
        IAIService: AIサービス実装
    """
    settings = get_settings()
    gemini_client = GeminiClient(
        project_id=settings.google_cloud_project,
        location=settings.google_cloud_location,
        model_name=settings.gemini_model_name,
    )
    return GeminiAIService(
        gemini_client=gemini_client,
        default_temperature=settings.gemini_temperature,
        default_max_output_tokens=settings.gemini_max_output_tokens,
        default_timeout_seconds=settings.gemini_timeout_seconds,
    )


async def get_ai_service_dependency() -> IAIService:
    """AIサービスの依存性

    Returns:
        IAIService: AIサービス
    """
    return get_ai_service()


# 将来的にデータベースセッションやリポジトリの依存性を追加予定
# 例:
# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     """データベースセッションの依存性"""
#     async with async_session_maker() as session:
#         yield session
