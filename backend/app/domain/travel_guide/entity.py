"""TravelGuide Aggregateのエンティティ"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from app.domain.shared.entity import Entity
from app.domain.travel_guide.value_objects import (
    Checkpoint,
    HistoricalEvent,
    MapData,
    SpotDetail,
)


def _validate_map_data(map_data: MapData) -> None:
    """地図データの最小バリデーションを行う

    Raises:
        ValueError: map_dataが不正な場合
    """
    if not isinstance(map_data, dict) or not map_data:
        raise ValueError("map_data is required and must be a non-empty dict.")

    center = map_data.get("center")
    if not isinstance(center, dict):
        raise ValueError("map_data.center must be a dict.")

    lat = center.get("lat")
    lng = center.get("lng")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        raise ValueError("map_data.center.lat must be a number.")
    if not isinstance(lng, (int, float)) or isinstance(lng, bool):
        raise ValueError("map_data.center.lng must be a number.")

    zoom = map_data.get("zoom")
    if not isinstance(zoom, int) or isinstance(zoom, bool):
        raise ValueError("map_data.zoom must be an int.")

    markers = map_data.get("markers")
    if not isinstance(markers, list) or not markers:
        raise ValueError("map_data.markers must be a non-empty list.")

    for marker in markers:
        if not isinstance(marker, dict):
            raise ValueError("map_data.markers must contain dict items.")

        marker_lat = marker.get("lat")
        marker_lng = marker.get("lng")
        label = marker.get("label")

        if not isinstance(marker_lat, (int, float)) or isinstance(marker_lat, bool):
            raise ValueError("marker.lat must be a number.")
        if not isinstance(marker_lng, (int, float)) or isinstance(marker_lng, bool):
            raise ValueError("marker.lng must be a number.")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("marker.label must be a non-empty string.")


def _copy_map_data(map_data: MapData) -> MapData:
    """地図データを防御的コピーする"""
    center = map_data.get("center", {})
    markers = map_data.get("markers", [])
    return cast(
        MapData,
        {
            **map_data,
            "center": dict(center),
            "markers": [dict(marker) for marker in markers],
        },
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
        map_data: MapData,
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
            map_data: 地図データ
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

        _validate_map_data(map_data)

        self._plan_id = plan_id
        self._overview = overview
        self._timeline = timeline
        self._spot_details = spot_details
        self._checkpoints = checkpoints
        self._map_data = _copy_map_data(map_data)
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
    def map_data(self) -> MapData:
        """地図データ"""
        return _copy_map_data(self._map_data)

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
        map_data: MapData | None = None,
    ) -> None:
        """旅行ガイドを更新する

        Args:
            overview: ガイド概要（オプション）
            timeline: 歴史イベント（オプション）
            spot_details: スポット詳細（オプション）
            checkpoints: チェックポイント（オプション）
            map_data: 地図データ（オプション）

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

        if map_data is not None:
            _validate_map_data(map_data)
            self._map_data = _copy_map_data(map_data)

        self._updated_at = datetime.now(UTC)
