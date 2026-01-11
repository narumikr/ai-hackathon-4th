"""API依存性注入の定義."""

from app.config.settings import Settings, get_settings


async def get_settings_dependency() -> Settings:
    """設定のシングルトンインスタンスを取得する依存性.

    Returns:
        Settings: アプリケーション設定
    """
    return get_settings()


# 将来的にデータベースセッションやリポジトリの依存性を追加予定
# 例:
# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     """データベースセッションの依存性"""
#     async with async_session_maker() as session:
#         yield session
