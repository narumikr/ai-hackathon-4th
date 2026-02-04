"""TravelGuideリポジトリの実装"""

import uuid

from sqlalchemy.orm import Session

from app.domain.travel_guide.entity import TravelGuide
from app.domain.travel_guide.repository import ITravelGuideRepository
from app.domain.travel_guide.value_objects import Checkpoint, HistoricalEvent, SpotDetail
from app.infrastructure.persistence.models import TravelGuideModel


class TravelGuideRepository(ITravelGuideRepository):
    """TravelGuideリポジトリのSQLAlchemy実装

    ドメインエンティティとSQLAlchemyモデル間のマッピングを行う
    """

    def __init__(self, session: Session):
        """リポジトリを初期化する

        Args:
            session: SQLAlchemyセッション
        """
        self._session = session

    def save(self, travel_guide: TravelGuide, *, commit: bool = True) -> TravelGuide:
        """TravelGuideを保存する

        Args:
            travel_guide: 保存するTravelGuideエンティティ
            commit: Trueの場合はトランザクションをコミットする

        Returns:
            TravelGuide: 保存されたTravelGuide（IDが割り当てられている）

        Raises:
            ValueError: 更新時にTravelGuideが見つからない場合
        """
        # ドメインエンティティ → SQLAlchemyモデル変換
        if travel_guide.id is None:
            # 新規作成
            model = TravelGuideModel(
                id=str(uuid.uuid4()),
                plan_id=travel_guide.plan_id,
                overview=travel_guide.overview,
                timeline=self._timeline_to_dict(travel_guide.timeline),
                spot_details=self._spot_details_to_dict(travel_guide.spot_details),
                checkpoints=self._checkpoints_to_dict(travel_guide.checkpoints),
            )
            self._session.add(model)
        else:
            # 更新
            model = self._session.get(TravelGuideModel, travel_guide.id)
            if model is None:
                raise ValueError(f"TravelGuide not found: {travel_guide.id}")

            model.overview = travel_guide.overview
            model.timeline = self._timeline_to_dict(travel_guide.timeline)
            model.spot_details = self._spot_details_to_dict(travel_guide.spot_details)
            model.checkpoints = self._checkpoints_to_dict(travel_guide.checkpoints)

        if commit:
            self._session.commit()
            self._session.refresh(model)
        else:
            self._session.flush()
            self._session.refresh(model)

        # SQLAlchemyモデル → ドメインエンティティ変換
        return self._to_entity(model)

    def find_by_id(self, guide_id: str) -> TravelGuide | None:
        """IDでTravelGuideを検索する

        Args:
            guide_id: 旅行ガイドID

        Returns:
            TravelGuide | None: 見つかった場合はTravelGuide、見つからない場合はNone
        """
        model = self._session.get(TravelGuideModel, guide_id)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_plan_id(self, plan_id: str) -> TravelGuide | None:
        """旅行計画IDでTravelGuideを検索する

        Args:
            plan_id: 旅行計画ID

        Returns:
            TravelGuide | None: 見つかった場合はTravelGuide、見つからない場合はNone
        """
        model = (
            self._session.query(TravelGuideModel)
            .filter(TravelGuideModel.plan_id == plan_id)
            .first()
        )
        if model is None:
            return None
        return self._to_entity(model)

    def delete(self, guide_id: str) -> None:
        """TravelGuideを削除する

        Args:
            guide_id: 削除する旅行ガイドID
        """
        model = self._session.get(TravelGuideModel, guide_id)
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: TravelGuideModel) -> TravelGuide:
        """SQLAlchemyモデル → ドメインエンティティ変換

        Args:
            model: SQLAlchemyモデル

        Returns:
            TravelGuide: ドメインエンティティ
        """
        # JSON型のtimelineを値オブジェクトに変換
        timeline = [
            HistoricalEvent(
                year=event["year"],
                event=event["event"],
                significance=event["significance"],
                related_spots=event["relatedSpots"],
            )
            for event in model.timeline
        ]

        # JSON型のspot_detailsを値オブジェクトに変換
        spot_details = [
            SpotDetail(
                spot_name=detail["spotName"],
                historical_background=detail["historicalBackground"],
                highlights=detail["highlights"],
                recommended_visit_time=detail["recommendedVisitTime"],
                historical_significance=detail["historicalSignificance"],
                image_url=detail.get("imageUrl"),  # デフォルトNone
                image_status=detail.get("imageStatus", "not_started"),  # デフォルト"not_started"
            )
            for detail in model.spot_details
        ]

        # JSON型のcheckpointsを値オブジェクトに変換
        checkpoints = [
            Checkpoint(
                spot_name=checkpoint["spotName"],
                checkpoints=checkpoint["checkpoints"],
                historical_context=checkpoint["historicalContext"],
            )
            for checkpoint in model.checkpoints
        ]

        return TravelGuide(
            id=model.id,
            plan_id=model.plan_id,
            overview=model.overview,
            timeline=timeline,
            spot_details=spot_details,
            checkpoints=checkpoints,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _timeline_to_dict(self, timeline: list[HistoricalEvent]) -> list[dict]:
        """HistoricalEvent → 辞書変換（JSON型で保存するため）

        Args:
            timeline: HistoricalEventリスト

        Returns:
            list[dict]: 辞書のリスト
        """
        return [
            {
                "year": event.year,
                "event": event.event,
                "significance": event.significance,
                "relatedSpots": list(event.related_spots),
            }
            for event in timeline
        ]

    def _spot_details_to_dict(self, spot_details: list[SpotDetail]) -> list[dict]:
        """SpotDetail → 辞書変換（JSON型で保存するため）

        Args:
            spot_details: SpotDetailリスト

        Returns:
            list[dict]: 辞書のリスト
        """
        return [
            {
                "spotName": detail.spot_name,
                "historicalBackground": detail.historical_background,
                "highlights": list(detail.highlights),
                "recommendedVisitTime": detail.recommended_visit_time,
                "historicalSignificance": detail.historical_significance,
                "imageUrl": detail.image_url,  # 新規追加
                "imageStatus": detail.image_status,  # 新規追加
            }
            for detail in spot_details
        ]

    def _checkpoints_to_dict(self, checkpoints: list[Checkpoint]) -> list[dict]:
        """Checkpoint → 辞書変換（JSON型で保存するため）

        Args:
            checkpoints: Checkpointリスト

        Returns:
            list[dict]: 辞書のリスト
        """
        return [
            {
                "spotName": checkpoint.spot_name,
                "checkpoints": list(checkpoint.checkpoints),
                "historicalContext": checkpoint.historical_context,
            }
            for checkpoint in checkpoints
        ]
