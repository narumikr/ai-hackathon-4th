"""振り返りリポジトリの実装"""

import uuid

from sqlalchemy.orm import Session

from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.repository import IReflectionRepository
from app.domain.reflection.value_objects import ImageAnalysis, ReflectionPamphlet, SpotReflection
from app.infrastructure.persistence.models import ReflectionModel, TravelPlanModel


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
                spot_notes=reflection.spot_notes,
                pamphlet=self._pamphlet_to_dict(reflection.pamphlet),
            )
            self._session.add(model)
        else:
            # 更新
            model = self._session.get(ReflectionModel, reflection.id)
            if model is None:
                raise ValueError(f"Reflection not found: {reflection.id}")

            model.photos = self._photos_to_dict(reflection.photos)
            model.user_notes = reflection.user_notes
            model.spot_notes = reflection.spot_notes
            model.pamphlet = self._pamphlet_to_dict(reflection.pamphlet)

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
            spot_id = self._resolve_spot_id(photo_data, model.plan_id)
            photo = Photo(
                id=photo_data["id"],
                spot_id=spot_id,
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
            spot_notes=model.spot_notes or {},
            pamphlet=self._pamphlet_from_dict(model.pamphlet),
            created_at=model.created_at,
        )

    def _resolve_spot_id(self, photo_data: dict, plan_id: str) -> str:
        """保存済み写真データからspotIdを解決する"""
        spot_id = photo_data.get("spotId")
        if isinstance(spot_id, str) and spot_id.strip():
            return spot_id.strip()

        analysis_data = photo_data.get("analysis") or {}
        detected_spots = analysis_data.get("detectedSpots")
        detected_names: list[str] = []
        if isinstance(detected_spots, list):
            for item in detected_spots:
                if isinstance(item, str) and item.strip():
                    detected_names.append(item.strip())

        if not detected_names:
            raise ValueError("spotId is required in stored photo data.")

        plan = self._session.get(TravelPlanModel, plan_id)
        if plan is None:
            raise ValueError(f"Travel plan not found for reflection: {plan_id}")

        name_to_id: dict[str, str] = {}
        for spot in plan.spots or []:
            name = getattr(spot, "name", None)
            spot_id_value = getattr(spot, "id", None)
            if isinstance(name, str) and name.strip() and isinstance(spot_id_value, str):
                name_to_id[name.strip()] = spot_id_value.strip()

        for name in detected_names:
            inferred_id = name_to_id.get(name)
            if inferred_id:
                return inferred_id

        raise ValueError("spotId is missing and could not be inferred from detected spots.")

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
                "spotId": photo.spot_id,
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

    @staticmethod
    def _pamphlet_to_dict(pamphlet: ReflectionPamphlet | None) -> dict | None:
        """パンフレットを辞書に変換する"""
        if pamphlet is None:
            return None
        return {
            "travel_summary": pamphlet.travel_summary,
            "spot_reflections": [
                {
                    "spotName": item["spot_name"],
                    "reflection": item["reflection"],
                }
                for item in pamphlet.spot_reflections
            ],
            "next_trip_suggestions": list(pamphlet.next_trip_suggestions),
        }

    @staticmethod
    def _pamphlet_from_dict(data: dict | None) -> ReflectionPamphlet | None:
        """辞書からパンフレットを復元する"""
        if data is None:
            return None
        if not isinstance(data, dict):
            raise ValueError("pamphlet must be a dict.")

        travel_summary = data.get("travel_summary")
        if not isinstance(travel_summary, str) or not travel_summary.strip():
            raise ValueError("pamphlet.travel_summary must be a non-empty string.")

        spot_reflections_data = data.get("spot_reflections")
        if not isinstance(spot_reflections_data, list):
            raise ValueError("pamphlet.spot_reflections must be a list.")

        spot_reflections: list[SpotReflection] = []
        for index, item in enumerate(spot_reflections_data):
            if not isinstance(item, dict):
                raise ValueError(f"pamphlet.spot_reflections[{index}] must be a dict.")
            spot_name = item.get("spotName")
            reflection = item.get("reflection")
            if not isinstance(spot_name, str) or not spot_name.strip():
                raise ValueError(
                    f"pamphlet.spot_reflections[{index}].spotName must be a non-empty string."
                )
            if not isinstance(reflection, str) or not reflection.strip():
                raise ValueError(
                    f"pamphlet.spot_reflections[{index}].reflection must be a non-empty string."
                )
            spot_reflections.append(
                {
                    "spot_name": spot_name.strip(),
                    "reflection": reflection.strip(),
                }
            )

        next_trip_suggestions = data.get("next_trip_suggestions")
        if not isinstance(next_trip_suggestions, list):
            raise ValueError("pamphlet.next_trip_suggestions must be a list.")

        return ReflectionPamphlet(
            travel_summary=travel_summary.strip(),
            spot_reflections=tuple(spot_reflections),
            next_trip_suggestions=tuple(next_trip_suggestions),
        )
