"""API依存性注入の定義."""

from functools import lru_cache

from app.application.ports.storage_service import IStorageService
from app.config.settings import Settings, get_settings
from app.infrastructure.storage.factory import create_storage_service


async def get_settings_dependency() -> Settings:
    """設定のシングルトンインスタンスを取得する依存性.

    Returns:
        Settings: アプリケーション設定
    """
    return get_settings()


@lru_cache
def get_storage_service() -> IStorageService:
    """ストレージサービスのシングルトンインスタンスを取得する.

    Returns:
        IStorageService: ストレージサービス実装
    """
    settings = get_settings()
    return create_storage_service(settings)


async def get_storage_service_dependency() -> IStorageService:
    """ストレージサービスの依存性.

    Returns:
        IStorageService: ストレージサービス
    """
    return get_storage_service()


# 将来的にデータベースセッションやリポジトリの依存性を追加予定
# 例:
# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     """データベースセッションの依存性"""
#     async with async_session_maker() as session:
#         yield session
