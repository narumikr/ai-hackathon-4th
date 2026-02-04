"""TravelGuide Aggregateの値オブジェクト"""

from dataclasses import dataclass

from app.domain.shared.value_object import ValueObject


def _normalize_str_list(value: list[str] | tuple[str, ...], field_name: str) -> tuple[str, ...]:
    """文字列リストをタプルに正規化する

    Raises:
        ValueError: 型や内容が不正な場合
    """
    if isinstance(value, list):
        normalized = tuple(value)
    elif isinstance(value, tuple):
        normalized = value
    else:
        raise ValueError(f"{field_name} must be a list or tuple of strings.")

    if not normalized:
        raise ValueError(f"{field_name} must not be empty.")

    if any(not isinstance(item, str) or not item.strip() for item in normalized):
        raise ValueError(f"{field_name} must contain non-empty strings only.")

    return normalized


@dataclass(frozen=True)
class HistoricalEvent(ValueObject):
    """歴史的イベント"""

    year: int
    event: str
    significance: str
    related_spots: tuple[str, ...]

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 必須フィールドの検証
        """
        if not isinstance(self.year, int) or isinstance(self.year, bool):
            raise ValueError("year must be an int.")

        if not self.event or not self.event.strip():
            raise ValueError("event is required and must not be empty.")

        if not self.significance or not self.significance.strip():
            raise ValueError("significance is required and must not be empty.")

        normalized = _normalize_str_list(self.related_spots, "related_spots")
        object.__setattr__(self, "related_spots", normalized)


@dataclass(frozen=True)
class SpotDetail(ValueObject):
    """スポット詳細"""

    spot_name: str
    historical_background: str
    highlights: tuple[str, ...]
    recommended_visit_time: str
    historical_significance: str
    image_url: str | None = None
    image_status: str = "not_started"

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 必須フィールドの検証
        """
        if not self.spot_name or not self.spot_name.strip():
            raise ValueError("spot_name is required and must not be empty.")

        if not self.historical_background or not self.historical_background.strip():
            raise ValueError("historical_background is required and must not be empty.")

        if not self.recommended_visit_time or not self.recommended_visit_time.strip():
            raise ValueError("recommended_visit_time is required and must not be empty.")

        if not self.historical_significance or not self.historical_significance.strip():
            raise ValueError("historical_significance is required and must not be empty.")

        normalized = _normalize_str_list(self.highlights, "highlights")
        object.__setattr__(self, "highlights", normalized)

        # 画像ステータスのバリデーション
        valid_statuses = {"not_started", "processing", "succeeded", "failed"}
        if self.image_status not in valid_statuses:
            raise ValueError(
                f"image_status must be one of {valid_statuses}, got: {self.image_status}"
            )


@dataclass(frozen=True)
class Checkpoint(ValueObject):
    """チェックポイント"""

    spot_name: str
    checkpoints: tuple[str, ...]
    historical_context: str

    def __post_init__(self) -> None:
        """バリデーション

        早期失敗: 必須フィールドの検証
        """
        if not self.spot_name or not self.spot_name.strip():
            raise ValueError("spot_name is required and must not be empty.")

        if not self.historical_context or not self.historical_context.strip():
            raise ValueError("historical_context is required and must not be empty.")

        normalized = _normalize_str_list(self.checkpoints, "checkpoints")
        object.__setattr__(self, "checkpoints", normalized)


def update_spot_image(
    spot_detail: SpotDetail,
    image_url: str | None,
    image_status: str,
) -> SpotDetail:
    """スポット画像情報を更新した新しいSpotDetailを生成する

    Args:
        spot_detail: 更新元のSpotDetail
        image_url: 画像URL（署名付きURL）
        image_status: 画像生成ステータス

    Returns:
        SpotDetail: 画像情報が更新された新しいSpotDetailインスタンス

    Raises:
        ValueError: image_statusが不正な値の場合
    """
    return SpotDetail(
        spot_name=spot_detail.spot_name,
        historical_background=spot_detail.historical_background,
        highlights=spot_detail.highlights,
        recommended_visit_time=spot_detail.recommended_visit_time,
        historical_significance=spot_detail.historical_significance,
        image_url=image_url,
        image_status=image_status,
    )
