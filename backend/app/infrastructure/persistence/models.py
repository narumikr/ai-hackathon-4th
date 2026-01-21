"""SQLAlchemyモデル定義."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base


class TravelPlanModel(Base):
    """旅行計画モデル."""

    __tablename__ = "travel_plans"

    # 主キー
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # 基本情報
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)

    # 観光スポット（JSON型）
    # 形式: List[{"id": str, "name": str, "location": {"lat": float, "lng": float}, "description": str, "userNotes": str}]
    spots: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # ステータス
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="planning",
        index=True,
    )
    guide_generation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="not_started",
    )
    reflection_generation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="not_started",
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    # リレーションシップ
    guide: Mapped["TravelGuideModel | None"] = relationship(
        "TravelGuideModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        uselist=False,
    )
    reflection: Mapped["ReflectionModel | None"] = relationship(
        "ReflectionModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        uselist=False,
    )

    # インデックス
    __table_args__ = (Index("ix_travel_plans_user_id_status", "user_id", "status"),)

    def __repr__(self) -> str:
        """文字列表現."""
        return (
            f"<TravelPlanModel(id={self.id}, "
            f"title={self.title}, "
            f"destination={self.destination}, "
            f"status={self.status})>"
        )


class TravelGuideModel(Base):
    """旅行ガイドモデル."""

    __tablename__ = "travel_guides"

    # 主キー
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # 外部キー
    plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("travel_plans.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # ガイド内容
    overview: Mapped[str] = mapped_column(Text, nullable=False)

    # 歴史的イベント（JSON型）
    # 形式: List[{"year": int, "event": str, "significance": str, "relatedSpots": List[str]}]
    timeline: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # スポット詳細（JSON型）
    # 形式: List[{"spotName": str, "historicalBackground": str, "highlights": List[str], "recommendedVisitTime": str, "historicalSignificance": str}]
    spot_details: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # チェックポイント（JSON型）
    # 形式: List[{"spotName": str, "checkpoints": List[str], "historicalContext": str}]
    checkpoints: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # 地図データ（JSON型）
    # 形式: {"center": {"lat": float, "lng": float}, "zoom": int, "markers": List[...]}
    map_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # リレーションシップ
    plan: Mapped["TravelPlanModel"] = relationship(
        "TravelPlanModel",
        back_populates="guide",
    )

    def __repr__(self) -> str:
        """文字列表現."""
        return f"<TravelGuideModel(id={self.id}, plan_id={self.plan_id})>"


class ReflectionModel(Base):
    """振り返りモデル."""

    __tablename__ = "reflections"

    # 主キー
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    # 外部キー
    plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("travel_plans.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # ユーザー情報
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # 写真（JSON型）
    # 形式: List[{"id": str, "spotId": str, "url": str, "analysis": {"detectedSpots": List[str], "historicalElements": List[str], "landmarks": List[str], "confidence": float}, "userDescription": str}]
    photos: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # スポットごとのメモ（JSON型）
    # 形式: Dict[str, Optional[str]]
    spot_notes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # ユーザーメモ
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    # リレーションシップ
    plan: Mapped["TravelPlanModel"] = relationship(
        "TravelPlanModel",
        back_populates="reflection",
    )

    def __repr__(self) -> str:
        """文字列表現."""
        return f"<ReflectionModel(id={self.id}, plan_id={self.plan_id}, user_id={self.user_id})>"
