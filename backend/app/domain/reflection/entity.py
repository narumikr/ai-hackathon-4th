"""Reflection Aggregateのエンティティ"""

from datetime import UTC, datetime

from app.domain.reflection.value_objects import ImageAnalysis
from app.domain.shared.entity import Entity


class Photo(Entity):
    """写真（エンティティ）."""

    def __init__(
        self,
        id: str,
        url: str,
        analysis: ImageAnalysis,
        user_description: str | None = None,
    ):
        """Photoを初期化する.

        Args:
            id: 写真ID
            url: 画像URL
            analysis: 画像分析結果
            user_description: ユーザー説明

        Raises:
            ValueError: 必須フィールドが空の場合
        """
        super().__init__(id)

        if not id or not id.strip():
            raise ValueError("id is required and must not be empty.")

        if not url or not url.strip():
            raise ValueError("url is required and must not be empty.")

        if not isinstance(analysis, ImageAnalysis):
            raise ValueError("analysis must be an ImageAnalysis instance.")

        if user_description is not None and not user_description.strip():
            raise ValueError("user_description cannot be empty.")

        self._url = url
        self._analysis = analysis
        self._user_description = user_description

    @property
    def url(self) -> str:
        """画像URL."""
        return self._url

    @property
    def analysis(self) -> ImageAnalysis:
        """画像分析結果."""
        return self._analysis

    @property
    def user_description(self) -> str | None:
        """ユーザー説明."""
        return self._user_description


class Reflection(Entity):
    """振り返り（Aggregate Root）

    旅行後の振り返り情報を表すドメインエンティティ
    """

    def __init__(
        self,
        plan_id: str,
        user_id: str,
        photos: list[Photo],
        user_notes: str | None = None,
        id: str | None = None,
        created_at: datetime | None = None,
    ):
        """Reflectionを初期化する.

        Args:
            plan_id: 旅行計画ID
            user_id: ユーザーID
            photos: 写真リスト
            user_notes: ユーザーメモ
            id: 振り返りID（Noneの場合は新規）
            created_at: 作成日時（Noneの場合は現在時刻）

        Raises:
            ValueError: 必須フィールドが空の場合
        """
        super().__init__(id)

        if not plan_id or not plan_id.strip():
            raise ValueError("plan_id is required and must not be empty.")

        if not user_id or not user_id.strip():
            raise ValueError("user_id is required and must not be empty.")

        if not isinstance(photos, list) or not photos:
            raise ValueError("photos must be a non-empty list.")

        if not all(isinstance(photo, Photo) for photo in photos):
            raise ValueError("photos must contain Photo items only.")

        if user_notes is not None and not user_notes.strip():
            raise ValueError("user_notes cannot be empty.")

        photo_ids = [photo.id for photo in photos]
        if len(set(photo_ids)) != len(photo_ids):
            raise ValueError("photos contains duplicate photo id.")

        self._plan_id = plan_id
        self._user_id = user_id
        self._photos = photos
        self._user_notes = user_notes
        self._created_at = created_at or datetime.now(UTC)

    @property
    def plan_id(self) -> str:
        """旅行計画ID."""
        return self._plan_id

    @property
    def user_id(self) -> str:
        """ユーザーID."""
        return self._user_id

    @property
    def photos(self) -> list[Photo]:
        """写真リスト（防御的コピー）."""
        return list(self._photos)

    @property
    def user_notes(self) -> str | None:
        """ユーザーメモ."""
        return self._user_notes

    @property
    def created_at(self) -> datetime:
        """作成日時."""
        return self._created_at

    def add_photo(self, photo: Photo) -> None:
        """写真を追加する.

        Args:
            photo: 追加する写真

        Raises:
            ValueError: 写真が不正な場合
        """
        if not isinstance(photo, Photo):
            raise ValueError("photo must be a Photo instance.")

        if any(existing.id == photo.id for existing in self._photos):
            raise ValueError("photo id already exists in photos.")

        self._photos.append(photo)

    def update_notes(self, user_notes: str | None) -> None:
        """ユーザーメモを更新する.

        Args:
            user_notes: 新しいメモ内容

        Raises:
            ValueError: 空文字列が渡された場合
        """
        if user_notes is not None and not user_notes.strip():
            raise ValueError("user_notes cannot be empty.")

        self._user_notes = user_notes
