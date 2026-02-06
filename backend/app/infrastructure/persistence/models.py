"""SQLAlchemyモデル定義."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
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
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # リレーションシップ
    spots: Mapped[list["TravelPlanSpotModel"]] = relationship(
        "TravelPlanSpotModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        order_by="TravelPlanSpotModel.sort_order",
    )
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


class TravelPlanSpotModel(Base):
    """旅行計画の観光スポットモデル."""

    __tablename__ = "travel_plan_spots"

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
        nullable=False,
        index=True,
    )

    # 観光スポット情報
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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
        back_populates="spots",
    )

    # インデックス
    __table_args__ = (Index("ix_travel_plan_spots_plan_id_sort_order", "plan_id", "sort_order"),)

    def __repr__(self) -> str:
        """文字列表現."""
        return f"<TravelPlanSpotModel(id={self.id}, plan_id={self.plan_id}, name={self.name})>"


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
    # 形式: List[{"id": str, "spotId": str, "url": str, "analysis": str, "userDescription": str}]
    photos: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # スポットごとのメモ（JSON型）
    # 形式: Dict[str, Optional[str]]
    spot_notes: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # ユーザーメモ
    user_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # パンフレット（JSON型）
    # 形式: {"travel_summary": str, "spot_reflections": List[{"spotName": str, "reflection": str}], "next_trip_suggestions": List[str]}
    pamphlet: Mapped[dict | None] = mapped_column(JSON, nullable=True)

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
        back_populates="reflection",
    )

    def __repr__(self) -> str:
        """文字列表現."""
        return f"<ReflectionModel(id={self.id}, plan_id={self.plan_id}, user_id={self.user_id})>"


class SpotImageJobModel(Base):
    """スポット画像生成ジョブモデル."""

    __tablename__ = "spot_image_jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    plan_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    spot_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

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
    locked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    locked_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        Index(
            "ux_spot_image_jobs_plan_spot",
            "plan_id",
            "spot_name",
            unique=True,
        ),
        Index("ix_spot_image_jobs_status_locked_at", "status", "locked_at"),
    )

    def __repr__(self) -> str:
        """文字列表現."""
        return (
            f"<SpotImageJobModel(id={self.id}, plan_id={self.plan_id}, "
            f"spot_name={self.spot_name}, status={self.status})>"
        )
