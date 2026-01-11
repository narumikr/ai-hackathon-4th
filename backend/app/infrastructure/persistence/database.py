"""データベース接続とセッション管理."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config.settings import get_settings

# 設定を取得
settings = get_settings()

# SQLAlchemyエンジンの作成
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # デバッグモードでSQLログを出力
    pool_pre_ping=True,  # 接続の健全性チェック
)

# セッションファクトリの作成
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """SQLAlchemyモデルのベースクラス."""

    pass


def create_tables() -> None:
    """データベーステーブルを作成する.

    開発環境でのみ使用することを推奨します。
    本番環境ではAlembicマイグレーションを使用してください。
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """データベーステーブルを削除する.

    警告: すべてのデータが削除されます。
    開発環境でのみ使用してください。
    """
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """データベースセッションを取得する依存性注入関数.

    FastAPIのDependsで使用されます。

    Yields:
        Session: データベースセッション

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
