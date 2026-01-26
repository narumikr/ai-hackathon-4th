"""振り返り集約のエンティティ"""

from datetime import UTC, datetime

from app.domain.reflection.value_objects import ImageAnalysis, ReflectionPamphlet
from app.domain.shared.entity import Entity


class Photo(Entity):
    """写真（エンティティ）"""

    def __init__(
        self,
        id: str,
        spot_id: str,
        url: str,
        analysis: ImageAnalysis,
        user_description: str | None = None,
    ):
        """Photoを初期化する

        Args:
            id: 写真ID
            spot_id: スポットID
            url: 画像URL
            analysis: 画像分析結果
            user_description: ユーザー説明

        Raises:
            ValueError: 必須フィールドが空の場合
        """
        super().__init__(id)

        if not id or not id.strip():
            raise ValueError("id is required and must not be empty.")

        if not spot_id or not spot_id.strip():
            raise ValueError("spot_id is required and must not be empty.")

        if not url or not url.strip():
            raise ValueError("url is required and must not be empty.")

        if not isinstance(analysis, ImageAnalysis):
            raise ValueError("analysis must be an ImageAnalysis instance.")

        if user_description is not None and not user_description.strip():
            raise ValueError("user_description cannot be empty.")

        self._spot_id = spot_id
        self._url = url
        self._analysis = analysis
        self._user_description = user_description

    @property
    def url(self) -> str:
        """画像URL"""
        return self._url

    @property
    def spot_id(self) -> str:
        """スポットID"""
        return self._spot_id

    @property
    def analysis(self) -> ImageAnalysis:
        """画像分析結果"""
        return self._analysis

    @property
    def user_description(self) -> str | None:
        """ユーザー説明"""
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
        spot_notes: dict[str, str | None] | None = None,
        pamphlet: ReflectionPamphlet | None = None,
        id: str | None = None,
        created_at: datetime | None = None,
    ):
        """振り返りを初期化する

        Args:
            plan_id: 旅行計画ID
            user_id: ユーザーID
            photos: 写真リスト
            user_notes: ユーザーメモ
            spot_notes: スポットごとのメモ
            pamphlet: 振り返りパンフレット
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

        notes = spot_notes or {}
        if not isinstance(notes, dict):
            raise ValueError("spot_notes must be a dict.")
        normalized_notes: dict[str, str | None] = {}
        for spot_id, note in notes.items():
            if not isinstance(spot_id, str) or not spot_id.strip():
                raise ValueError("spot_notes key must be a non-empty string.")
            if note is not None and not isinstance(note, str):
                raise ValueError("spot_notes value must be a string or None.")
            if isinstance(note, str) and not note.strip():
                raise ValueError("spot_notes value cannot be empty.")
            normalized_notes[spot_id] = note.strip() if isinstance(note, str) else None

        if pamphlet is not None and not isinstance(pamphlet, ReflectionPamphlet):
            raise ValueError("pamphlet must be a ReflectionPamphlet instance or None.")

        self._plan_id = plan_id
        self._user_id = user_id
        self._photos = photos
        self._user_notes = user_notes
        self._spot_notes = normalized_notes
        self._pamphlet = pamphlet
        self._created_at = created_at or datetime.now(UTC)

    @property
    def plan_id(self) -> str:
        """旅行計画ID"""
        return self._plan_id

    @property
    def user_id(self) -> str:
        """ユーザーID"""
        return self._user_id

    @property
    def photos(self) -> list[Photo]:
        """写真リスト（防御的コピー）"""
        return list(self._photos)

    @property
    def user_notes(self) -> str | None:
        """ユーザーメモ"""
        return self._user_notes

    @property
    def spot_notes(self) -> dict[str, str | None]:
        """スポットごとのメモ"""
        return dict(self._spot_notes)

    @property
    def created_at(self) -> datetime:
        """作成日時"""
        return self._created_at

    @property
    def pamphlet(self) -> ReflectionPamphlet | None:
        """振り返りパンフレット"""
        return self._pamphlet

    def add_photo(self, photo: Photo) -> None:
        """写真を追加する

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
        """ユーザーメモを更新する

        Args:
            user_notes: 新しいメモ内容

        Raises:
            ValueError: 空文字列が渡された場合
        """
        if user_notes is not None and not user_notes.strip():
            raise ValueError("user_notes cannot be empty.")

        self._user_notes = user_notes

    def update_spot_note(self, spot_id: str, note: str | None) -> None:
        """スポットメモを更新する

        Args:
            spot_id: スポットID
            note: メモ内容

        Raises:
            ValueError: 入力が不正な場合
        """
        if not spot_id or not spot_id.strip():
            raise ValueError("spot_id is required and must not be empty.")
        if note is not None and not isinstance(note, str):
            raise ValueError("spot_note must be a string or None.")
        if note is None:
            self._spot_notes.pop(spot_id, None)
            return
        if isinstance(note, str) and not note.strip():
            raise ValueError("spot_note cannot be empty.")

        self._spot_notes[spot_id] = note.strip()

    def update_pamphlet(self, pamphlet: ReflectionPamphlet | None) -> None:
        """パンフレットを更新する

        Args:
            pamphlet: パンフレット

        Raises:
            ValueError: パンフレットが不正な場合
        """
        if pamphlet is not None and not isinstance(pamphlet, ReflectionPamphlet):
            raise ValueError("pamphlet must be a ReflectionPamphlet instance or None.")
        self._pamphlet = pamphlet
