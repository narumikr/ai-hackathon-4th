"""振り返りリポジトリの実装"""

import uuid

from sqlalchemy.orm import Session

from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.repository import IReflectionRepository
from app.domain.reflection.value_objects import ImageAnalysis
from app.infrastructure.persistence.models import ReflectionModel


class ReflectionRepository(IReflectionRepository):
    """振り返りリポジトリのSQLAlchemy実装

    ドメインエンティティとSQLAlchemyモデル間のマッピングを行う
    """

    def __init__(self, session: Session):
        """リポジトリを初期化する

        Args:
            session: SQLAlchemyセッション
        """
        self._session = session

    def save(self, reflection: Reflection) -> Reflection:
        """振り返りを保存する

        Args:
            reflection: 保存する振り返りエンティティ

        Returns:
            Reflection: 保存された振り返り（IDが割り当てられている）

        Raises:
            ValueError: 更新時に振り返りが見つからない場合
        """
        # ドメインエンティティ → SQLAlchemyモデル変換
        if reflection.id is None:
            # 新規作成
            model = ReflectionModel(
                id=str(uuid.uuid4()),
                plan_id=reflection.plan_id,
                user_id=reflection.user_id,
                photos=self._photos_to_dict(reflection.photos),
                user_notes=reflection.user_notes,
            )
            self._session.add(model)
        else:
            # 更新
            model = self._session.get(ReflectionModel, reflection.id)
            if model is None:
                raise ValueError(f"Reflection not found: {reflection.id}")

            model.photos = self._photos_to_dict(reflection.photos)
            model.user_notes = reflection.user_notes

        self._session.commit()
        self._session.refresh(model)

        # SQLAlchemyモデル → ドメインエンティティ変換
        return self._to_entity(model)

    def find_by_id(self, reflection_id: str) -> Reflection | None:
        """IDで振り返りを検索する

        Args:
            reflection_id: 振り返りID

        Returns:
            Reflection | None: 見つかった場合は振り返り、見つからない場合はNone
        """
        model = self._session.get(ReflectionModel, reflection_id)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_plan_id(self, plan_id: str) -> Reflection | None:
        """旅行計画IDで振り返りを検索する

        Args:
            plan_id: 旅行計画ID

        Returns:
            Reflection | None: 見つかった場合は振り返り、見つからない場合はNone
        """
        model = (
            self._session.query(ReflectionModel).filter(ReflectionModel.plan_id == plan_id).first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def delete(self, reflection_id: str) -> None:
        """振り返りを削除する

        Args:
            reflection_id: 削除する振り返りID
        """
        model = self._session.get(ReflectionModel, reflection_id)
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: ReflectionModel) -> Reflection:
        """SQLAlchemyモデル → ドメインエンティティ変換

        Args:
            model: SQLAlchemyモデル

        Returns:
            Reflection: ドメインエンティティ
        """
        # JSON型のphotosをPhotoエンティティに変換
        photos = []
        for photo_data in model.photos:
            analysis_data = photo_data["analysis"]
            analysis = ImageAnalysis(
                detected_spots=analysis_data.get("detectedSpots", []),
                historical_elements=analysis_data.get("historicalElements", []),
                landmarks=analysis_data.get("landmarks", []),
                confidence=analysis_data["confidence"],
            )
            photo = Photo(
                id=photo_data["id"],
                url=photo_data["url"],
                analysis=analysis,
                user_description=photo_data.get("userDescription"),
            )
            photos.append(photo)

        return Reflection(
            id=model.id,
            plan_id=model.plan_id,
            user_id=model.user_id,
            photos=photos,
            user_notes=model.user_notes,
            created_at=model.created_at,
        )

    def _photos_to_dict(self, photos: list[Photo]) -> list[dict]:
        """Photo → 辞書変換（JSON型で保存するため）

        Args:
            photos: Photoリスト

        Returns:
            list[dict]: 辞書のリスト
        """
        return [
            {
                "id": photo.id,
                "url": photo.url,
                "analysis": {
                    "detectedSpots": list(photo.analysis.detected_spots),
                    "historicalElements": list(photo.analysis.historical_elements),
                    "landmarks": list(photo.analysis.landmarks),
                    "confidence": photo.analysis.confidence,
                },
                "userDescription": photo.user_description,
            }
            for photo in photos
        ]
