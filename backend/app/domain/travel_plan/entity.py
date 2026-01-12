"""TravelPlan Aggregateのエンティティ"""

from datetime import UTC, datetime

from app.domain.shared.entity import Entity
from app.domain.travel_plan.value_objects import Location, PlanStatus


class TouristSpot(Entity):
    """観光スポット（エンティティ）."""

    def __init__(
        self,
        id: str,
        name: str,
        location: Location,
        description: str | None = None,
        user_notes: str | None = None,
    ):
        """TouristSpotを初期化する.

        Args:
            id: 観光スポットID
            name: スポット名
            location: 位置情報
            description: 説明
            user_notes: ユーザーメモ

        Raises:
            ValueError: 必須フィールドが空の場合
        """
        super().__init__(id)

        # 早期失敗: 必須フィールドの検証
        if not id or not id.strip():
            raise ValueError("id is required and must not be empty.")

        if not name or not name.strip():
            raise ValueError("Tourist spot name is required and must not be empty.")

        if not isinstance(location, Location):
            raise ValueError("location must be a Location instance.")

        self._name = name
        self._location = location
        self._description = description
        self._user_notes = user_notes

    @property
    def name(self) -> str:
        """スポット名."""
        return self._name

    @property
    def location(self) -> Location:
        """位置情報."""
        return self._location

    @property
    def description(self) -> str | None:
        """説明."""
        return self._description

    @property
    def user_notes(self) -> str | None:
        """ユーザーメモ."""
        return self._user_notes


class TravelPlan(Entity):
    """旅行計画（Aggregate Root）

    旅行計画を表すドメインエンティティ
    ユーザー、目的地、観光スポットの情報を管理する
    """

    def __init__(
        self,
        user_id: str,
        title: str,
        destination: str,
        spots: list[TouristSpot],
        status: PlanStatus = PlanStatus.PLANNING,
        id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        """TravelPlanを初期化する.

        Args:
            user_id: ユーザーID
            title: 旅行タイトル
            destination: 目的地
            spots: 観光スポットリスト
            status: 旅行状態（デフォルト: PLANNING）
            id: 旅行計画ID（Noneの場合は新規）
            created_at: 作成日時（Noneの場合は現在時刻）
            updated_at: 更新日時（Noneの場合は現在時刻）

        Raises:
            ValueError: 必須フィールドが空の場合
        """
        super().__init__(id)

        # 早期失敗: 必須フィールドの検証
        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and must not be empty.")

        if not title or not title.strip():
            raise ValueError("title is required and must not be empty.")

        if not destination or not destination.strip():
            raise ValueError("destination is required and must not be empty.")

        self._user_id = user_id
        self._title = title
        self._destination = destination
        self._spots = spots
        self._status = status
        self._created_at = created_at or datetime.now(UTC)
        self._updated_at = updated_at or datetime.now(UTC)

    @property
    def user_id(self) -> str:
        """ユーザーID."""
        return self._user_id

    @property
    def title(self) -> str:
        """旅行タイトル."""
        return self._title

    @property
    def destination(self) -> str:
        """目的地."""
        return self._destination

    @property
    def spots(self) -> list[TouristSpot]:
        """観光スポットリスト（防御的コピー）."""
        return self._spots.copy()

    @property
    def status(self) -> PlanStatus:
        """旅行状態."""
        return self._status

    @property
    def created_at(self) -> datetime:
        """作成日時."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """更新日時."""
        return self._updated_at

    def update_plan(
        self,
        title: str | None = None,
        destination: str | None = None,
        spots: list[TouristSpot] | None = None,
    ) -> None:
        """旅行計画を更新する.

        Args:
            title: 旅行タイトル（オプション）
            destination: 目的地（オプション）
            spots: 観光スポットリスト（オプション）

        Raises:
            ValueError: 空文字列が渡された場合
        """
        if title is not None:
            if not title.strip():
                raise ValueError("title cannot be empty.")
            self._title = title

        if destination is not None:
            if not destination.strip():
                raise ValueError("destination cannot be empty.")
            self._destination = destination

        if spots is not None:
            self._spots = spots

        # updated_atを自動更新
        self._updated_at = datetime.now(UTC)

    def complete(self) -> None:
        """旅行を完了状態にする."""
        self._status = PlanStatus.COMPLETED
        self._updated_at = datetime.now(UTC)
