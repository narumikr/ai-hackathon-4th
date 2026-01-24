"""TravelGuide Aggregateのエンティティ"""

from __future__ import annotations

from datetime import UTC, datetime

from app.domain.shared.entity import Entity
from app.domain.travel_guide.value_objects import (
    Checkpoint,
    HistoricalEvent,
    SpotDetail,
)


class TravelGuide(Entity):
    """旅行ガイド（Aggregate Root）"""

    def __init__(
        self,
        plan_id: str,
        overview: str,
        timeline: list[HistoricalEvent],
        spot_details: list[SpotDetail],
        checkpoints: list[Checkpoint],
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        """TravelGuideを初期化する

        Args:
            plan_id: 旅行計画ID
            overview: ガイド概要
            timeline: 歴史イベント
            spot_details: スポット詳細
            checkpoints: チェックポイント
            id: ガイドID（Noneの場合は新規）
            created_at: 作成日時（Noneの場合は現在時刻）
            updated_at: 更新日時（Noneの場合は現在時刻）

        Raises:
            ValueError: 必須フィールドが空の場合
        """
        super().__init__(id)

        if not plan_id or not plan_id.strip():
            raise ValueError("plan_id is required and must not be empty.")

        if not overview or not overview.strip():
            raise ValueError("overview is required and must not be empty.")

        if not isinstance(timeline, list) or not timeline:
            raise ValueError("timeline must be a non-empty list.")

        if not all(isinstance(event, HistoricalEvent) for event in timeline):
            raise ValueError("timeline must contain HistoricalEvent items only.")

        if not isinstance(spot_details, list) or not spot_details:
            raise ValueError("spot_details must be a non-empty list.")

        if not all(isinstance(detail, SpotDetail) for detail in spot_details):
            raise ValueError("spot_details must contain SpotDetail items only.")

        if not isinstance(checkpoints, list) or not checkpoints:
            raise ValueError("checkpoints must be a non-empty list.")

        if not all(isinstance(checkpoint, Checkpoint) for checkpoint in checkpoints):
            raise ValueError("checkpoints must contain Checkpoint items only.")

        self._plan_id = plan_id
        self._overview = overview
        self._timeline = timeline
        self._spot_details = spot_details
        self._checkpoints = checkpoints
        # created_atとupdated_atが両方Noneの場合は同一の現在時刻を使用して一貫性を保つ
        if created_at is None and updated_at is None:
            now = datetime.now(UTC)
            self._created_at = now
            self._updated_at = now
        else:
            self._created_at = created_at or datetime.now(UTC)
            self._updated_at = updated_at or datetime.now(UTC)

    @property
    def plan_id(self) -> str:
        """旅行計画ID"""
        return self._plan_id

    @property
    def overview(self) -> str:
        """ガイド概要"""
        return self._overview

    @property
    def timeline(self) -> list[HistoricalEvent]:
        """歴史イベント"""
        return list(self._timeline)

    @property
    def spot_details(self) -> list[SpotDetail]:
        """スポット詳細"""
        return list(self._spot_details)

    @property
    def checkpoints(self) -> list[Checkpoint]:
        """チェックポイント"""
        return list(self._checkpoints)

    @property
    def created_at(self) -> datetime:
        """作成日時"""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """更新日時"""
        return self._updated_at

    def update_guide(
        self,
        overview: str | None = None,
        timeline: list[HistoricalEvent] | None = None,
        spot_details: list[SpotDetail] | None = None,
        checkpoints: list[Checkpoint] | None = None,
    ) -> None:
        """旅行ガイドを更新する

        Args:
            overview: ガイド概要（オプション）
            timeline: 歴史イベント（オプション）
            spot_details: スポット詳細（オプション）
            checkpoints: チェックポイント（オプション）

        Raises:
            ValueError: 空文字列が渡された場合
        """
        if overview is not None:
            if not overview.strip():
                raise ValueError("overview cannot be empty.")
            self._overview = overview

        if timeline is not None:
            if not isinstance(timeline, list) or not timeline:
                raise ValueError("timeline must be a non-empty list.")
            if not all(isinstance(event, HistoricalEvent) for event in timeline):
                raise ValueError("timeline must contain HistoricalEvent items only.")
            self._timeline = timeline

        if spot_details is not None:
            if not isinstance(spot_details, list) or not spot_details:
                raise ValueError("spot_details must be a non-empty list.")
            if not all(isinstance(detail, SpotDetail) for detail in spot_details):
                raise ValueError("spot_details must contain SpotDetail items only.")
            self._spot_details = spot_details

        if checkpoints is not None:
            if not isinstance(checkpoints, list) or not checkpoints:
                raise ValueError("checkpoints must be a non-empty list.")
            if not all(isinstance(checkpoint, Checkpoint) for checkpoint in checkpoints):
                raise ValueError("checkpoints must contain Checkpoint items only.")
            self._checkpoints = checkpoints

        self._updated_at = datetime.now(UTC)
