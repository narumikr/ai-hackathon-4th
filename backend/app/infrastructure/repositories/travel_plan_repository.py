"""TravelPlanリポジトリの実装."""

import uuid

from sqlalchemy.orm import Session

from app.domain.travel_plan.entity import TouristSpot, TravelPlan
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.domain.travel_plan.value_objects import GenerationStatus, PlanStatus
from app.infrastructure.persistence.models import TravelPlanModel, TravelPlanSpotModel


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

    def save(self, travel_plan: TravelPlan, *, commit: bool = True) -> TravelPlan:
        """TravelPlanを保存する.

        Args:
            travel_plan: 保存するTravelPlanエンティティ
            commit: Trueの場合はトランザクションをコミットする

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
                spots=self._spots_to_models(travel_plan.spots),
                status=travel_plan.status.value,
                guide_generation_status=travel_plan.guide_generation_status.value,
                reflection_generation_status=travel_plan.reflection_generation_status.value,
            )
            self._session.add(model)
        else:
            # 更新
            model = self._session.get(TravelPlanModel, travel_plan.id)
            if model is None:
                raise ValueError(f"TravelPlan not found: {travel_plan.id}")

            model.title = travel_plan.title
            model.destination = travel_plan.destination
            model.spots = self._spots_to_models(travel_plan.spots)
            model.status = travel_plan.status.value
            model.guide_generation_status = travel_plan.guide_generation_status.value
            model.reflection_generation_status = travel_plan.reflection_generation_status.value

        if commit:
            self._session.commit()
            self._session.refresh(model)
        else:
            self._session.flush()
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

    def begin_nested(self):
        """ネストされたトランザクション（セーブポイント）を開始する."""
        return self._session.begin_nested()

    def _to_entity(self, model: TravelPlanModel) -> TravelPlan:
        """SQLAlchemyモデル → ドメインエンティティ変換.

        Args:
            model: SQLAlchemyモデル

        Returns:
            TravelPlan: ドメインエンティティ
        """
        # テーブルのspotsを値オブジェクトに変換
        spots = []
        for spot in model.spots:
            spot_id = spot.id
            if spot_id is None or not str(spot_id).strip():
                raise ValueError("TouristSpot.id is required in persistence data.")

            spots.append(
                TouristSpot(
                    id=str(spot_id),
                    name=spot.name,
                    description=spot.description,
                    user_notes=spot.user_notes,
                )
            )

        return TravelPlan(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            destination=model.destination,
            spots=spots,
            status=PlanStatus(model.status),
            guide_generation_status=GenerationStatus(model.guide_generation_status),
            reflection_generation_status=GenerationStatus(model.reflection_generation_status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _spots_to_models(self, spots: list[TouristSpot]) -> list[TravelPlanSpotModel]:
        """TouristSpot → SQLAlchemyモデル変換.

        Args:
            spots: TouristSpotリスト

        Returns:
            list[TravelPlanSpotModel]: TravelPlanSpotModelリスト
        """
        return [
            TravelPlanSpotModel(
                id=spot.id,
                name=spot.name,
                description=spot.description,
                user_notes=spot.user_notes,
                sort_order=index,
            )
            for index, spot in enumerate(spots)
        ]
