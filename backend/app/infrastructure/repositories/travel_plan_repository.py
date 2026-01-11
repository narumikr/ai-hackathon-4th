"""TravelPlanリポジトリの実装."""

import uuid

from sqlalchemy.orm import Session

from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import Location, PlanStatus
from app.infrastructure.persistence.models import TravelPlanModel


class TravelPlanRepository(ITravelPlanRepository):
    """TravelPlanリポジトリのSQLAlchemy実装.

    ドメインエンティティとSQLAlchemyモデル間のマッピングを行う。
    """

    def __init__(self, session: Session):
        """リポジトリを初期化する.

        Args:
            session: SQLAlchemyセッション
        """
        self._session = session

    def save(self, travel_plan: TravelPlan) -> TravelPlan:
        """TravelPlanを保存する.

        Args:
            travel_plan: 保存するTravelPlanエンティティ

        Returns:
            TravelPlan: 保存されたTravelPlan（IDが割り当てられている）

        Raises:
            ValueError: 更新時にTravelPlanが見つからない場合
        """
        # ドメインエンティティ → SQLAlchemyモデル変換
        if travel_plan.id is None:
            # 新規作成
            model = TravelPlanModel(
                id=str(uuid.uuid4()),
                user_id=travel_plan.user_id,
                title=travel_plan.title,
                destination=travel_plan.destination,
                spots=self._spots_to_dict(travel_plan.spots),
                status=travel_plan.status.value,
            )
            self._session.add(model)
        else:
            # 更新
            model = self._session.get(TravelPlanModel, travel_plan.id)
            if model is None:
                raise ValueError(f"TravelPlan not found: {travel_plan.id}")

            model.title = travel_plan.title
            model.destination = travel_plan.destination
            model.spots = self._spots_to_dict(travel_plan.spots)
            model.status = travel_plan.status.value

        self._session.commit()
        self._session.refresh(model)

        # SQLAlchemyモデル → ドメインエンティティ変換
        return self._to_entity(model)

    def find_by_id(self, plan_id: str) -> TravelPlan | None:
        """IDでTravelPlanを検索する.

        Args:
            plan_id: 旅行計画ID

        Returns:
            TravelPlan | None: 見つかった場合はTravelPlan、見つからない場合はNone
        """
        model = self._session.get(TravelPlanModel, plan_id)
        if model is None:
            return None
        return self._to_entity(model)

    def find_by_user_id(self, user_id: str) -> list[TravelPlan]:
        """ユーザーIDでTravelPlanを検索する.

        Args:
            user_id: ユーザーID

        Returns:
            list[TravelPlan]: ユーザーの旅行計画リスト（見つからない場合は空リスト）
        """
        models = (
            self._session.query(TravelPlanModel).filter(TravelPlanModel.user_id == user_id).all()
        )
        return [self._to_entity(model) for model in models]

    def delete(self, plan_id: str) -> None:
        """TravelPlanを削除する.

        Args:
            plan_id: 削除する旅行計画ID
        """
        model = self._session.get(TravelPlanModel, plan_id)
        if model is not None:
            self._session.delete(model)
            self._session.commit()

    def _to_entity(self, model: TravelPlanModel) -> TravelPlan:
        """SQLAlchemyモデル → ドメインエンティティ変換.

        Args:
            model: SQLAlchemyモデル

        Returns:
            TravelPlan: ドメインエンティティ
        """
        # JSON型のspotsを値オブジェクトに変換
        spots = []
        for spot in model.spots:
            spot_id = spot.get("id")
            if spot_id is None or not str(spot_id).strip():
                raise ValueError("TouristSpot.id is required in persistence data.")

            spots.append(
                TouristSpot(
                    id=str(spot_id),
                    name=spot["name"],
                    location=Location(
                        lat=spot["location"]["lat"],
                        lng=spot["location"]["lng"],
                    ),
                    description=spot.get("description"),
                    user_notes=spot.get("userNotes"),
                )
            )

        return TravelPlan(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            destination=model.destination,
            spots=spots,
            status=PlanStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _spots_to_dict(self, spots: list[TouristSpot]) -> list[dict]:
        """TouristSpot → 辞書変換（JSON型で保存するため）.

        Args:
            spots: TouristSpotリスト

        Returns:
            list[dict]: 辞書のリスト
        """
        return [
            {
                "id": spot.id,
                "name": spot.name,
                "location": {
                    "lat": spot.location.lat,
                    "lng": spot.location.lng,
                },
                "description": spot.description,
                "userNotes": spot.user_notes,
            }
            for spot in spots
        ]
