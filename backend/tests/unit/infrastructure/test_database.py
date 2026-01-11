"""データベース接続とセッション管理のテスト."""

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import Base, engine


def test_engine_creation():
    """エンジンが正しく作成されることを確認する."""
    assert engine is not None
    assert str(engine.url).startswith("postgresql://")


def test_session_creation(db_session: Session):
    """セッションが正しく作成されることを確認する."""
    assert db_session is not None
    assert isinstance(db_session, Session)


def test_base_metadata():
    """Baseのメタデータが正しく設定されていることを確認する."""
    assert Base.metadata is not None

    # 3つのテーブルが定義されていることを確認
    table_names = [table.name for table in Base.metadata.tables.values()]
    assert "travel_plans" in table_names
    assert "travel_guides" in table_names
    assert "reflections" in table_names


def test_database_tables_exist(test_engine):
    """データベースにテーブルが存在することを確認する."""
    inspector = inspect(test_engine)
    table_names = inspector.get_table_names()

    assert "travel_plans" in table_names
    assert "travel_guides" in table_names
    assert "reflections" in table_names
