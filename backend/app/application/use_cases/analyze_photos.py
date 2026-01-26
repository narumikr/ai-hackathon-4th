"""写真分析ユースケース"""

from app.application.dto.reflection_dto import ReflectionDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.repository import IReflectionRepository
from app.domain.reflection.value_objects import ImageAnalysis
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository


def _require_str(value: object, field_name: str) -> str:
    """必須の文字列フィールドを検証する"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string.")
    return value.strip()


def _require_list(value: object, field_name: str) -> list:
    """必須の配列フィールドを検証する"""
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    return value


def _require_str_list(value: object, field_name: str) -> tuple[str, ...]:
    """文字列リストを検証する（空リストは許可）"""
    raw_items = _require_list(value, field_name)
    items: list[str] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string.")
        items.append(item.strip())
    return tuple(items)


def _require_confidence(value: object, field_name: str) -> float:
    """信頼度の数値フィールドを検証する"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a number.")
    confidence = float(value)
    if not 0 <= confidence <= 1:
        raise ValueError(f"{field_name} must be between 0 and 1.")
    return confidence


def _normalize_photo_inputs(photos: list[dict]) -> list[dict]:
    """写真入力を正規化し、早期失敗させる"""
    if not isinstance(photos, list) or not photos:
        raise ValueError("photos must be a non-empty list.")

    normalized: list[dict] = []
    seen_ids: set[str] = set()

    for index, photo in enumerate(photos):
        if not isinstance(photo, dict):
            raise ValueError(f"photos[{index}] must be a dict.")

        photo_id = _require_str(photo.get("id"), f"photos[{index}].id")
        if photo_id in seen_ids:
            raise ValueError(f"photos[{index}].id is duplicated: {photo_id}")
        seen_ids.add(photo_id)

        spot_id = _require_str(photo.get("spotId"), f"photos[{index}].spotId")

        url = _require_str(photo.get("url"), f"photos[{index}].url")

        user_description = photo.get("userDescription")
        if user_description is not None:
            if not isinstance(user_description, str) or not user_description.strip():
                raise ValueError(f"photos[{index}].userDescription must be a non-empty string.")
            user_description = user_description.strip()

        normalized.append(
            {
                "id": photo_id,
                "spotId": spot_id,
                "url": url,
                "userDescription": user_description,
            }
        )

    return normalized


# 画像分析の構造化出力スキーマ（検出スポット/歴史要素/ランドマーク/信頼度）。
_IMAGE_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "detectedSpots": {"type": "array", "items": {"type": "string"}},
        "historicalElements": {"type": "array", "items": {"type": "string"}},
        "landmarks": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["detectedSpots", "historicalElements", "landmarks", "confidence"],
    "additionalProperties": False,
}


def _parse_image_analysis_data(data: object, *, index: int) -> ImageAnalysis:
    """AIの画像分析レスポンスをパースする"""
    if not isinstance(data, dict):
        raise ValueError(f"photos[{index}].analysis response must be a JSON object.")

    detected_spots = _require_str_list(
        data.get("detectedSpots"),
        f"photos[{index}].analysis.detectedSpots",
    )
    historical_elements = _require_str_list(
        data.get("historicalElements"),
        f"photos[{index}].analysis.historicalElements",
    )
    landmarks = _require_str_list(
        data.get("landmarks"),
        f"photos[{index}].analysis.landmarks",
    )
    confidence = _require_confidence(
        data.get("confidence"),
        f"photos[{index}].analysis.confidence",
    )

    return ImageAnalysis(
        detected_spots=detected_spots,
        historical_elements=historical_elements,
        landmarks=landmarks,
        confidence=confidence,
    )


def _build_image_analysis_prompt(
    destination: str,
    spot_name: str,
    user_description: str | None,
) -> str:
    """画像分析のプロンプトを生成する"""
    description_text = ""
    if user_description:
        description_text = f"ユーザーの補足説明: {user_description}\n"
    return (
        "次の旅行先と観光スポット情報を参考に、画像に写っている観光スポットや歴史的要素を特定してください。\n"
        f"旅行先: {destination}\n"
        "観光スポット:\n"
        f"- {spot_name}\n"
        f"{description_text}"
        "出力はJSONのみで返してください。\n"
        "必須キー: detectedSpots, historicalElements, landmarks, confidence\n"
        "detectedSpots/historicalElements/landmarksは文字列の配列、confidenceは0から1の数値です。\n"
    )


class AnalyzePhotosUseCase:
    """写真分析ユースケース

    旅行計画に紐づく写真をAIで分析し振り返りとして保存する
    """

    def __init__(
        self,
        plan_repository: ITravelPlanRepository,
        reflection_repository: IReflectionRepository,
        ai_service: IAIService,
    ) -> None:
        """ユースケースを初期化する

        Args:
            plan_repository: TravelPlanリポジトリ
            reflection_repository: 振り返りリポジトリ
            ai_service: AIサービス
        """
        self._plan_repository = plan_repository
        self._reflection_repository = reflection_repository
        self._ai_service = ai_service

    async def execute(
        self,
        plan_id: str,
        user_id: str,
        photos: list[dict],
        spot_note: str | None = None,
        spot_note_provided: bool = False,
    ) -> ReflectionDTO:
        """写真を分析し振り返りを保存する

        Args:
            plan_id: 旅行計画ID
            user_id: ユーザーID
            photos: 写真リスト（辞書形式）
            spot_note: スポットの感想
            spot_note_provided: フォームでspotNoteが送信されたかどうか

        Returns:
            ReflectionDTO: 保存された振り返り

        Raises:
            TravelPlanNotFoundError: 旅行計画が見つからない場合
            ValueError: バリデーションエラー
        """
        validate_required_str(plan_id, "plan_id")
        validate_required_str(user_id, "user_id")
        if spot_note is not None:
            spot_note = spot_note.strip()
            if not spot_note:
                spot_note = None

        normalized_photos = _normalize_photo_inputs(photos)
        spot_ids = {photo["spotId"] for photo in normalized_photos}
        if len(spot_ids) != 1:
            raise ValueError("photos must belong to a single spot.")
        spot_id = next(iter(spot_ids))

        travel_plan = self._plan_repository.find_by_id(plan_id)
        if travel_plan is None:
            raise TravelPlanNotFoundError(plan_id)

        if travel_plan.user_id != user_id:
            raise ValueError("user_id does not match the travel plan owner.")

        existing_reflection = self._reflection_repository.find_by_plan_id(plan_id)
        existing_photo_ids: set[str] = set()
        if existing_reflection is not None:
            if existing_reflection.user_id != user_id:
                raise ValueError("user_id does not match the reflection owner.")
            for photo in existing_reflection.photos:
                if photo.id is None:
                    raise ValueError("photo id is required.")
                existing_photo_ids.add(photo.id)

        plan_spots_by_id = {spot.id: spot for spot in travel_plan.spots}
        new_photos: list[Photo] = []
        for index, photo in enumerate(normalized_photos):
            photo_id = photo["id"]
            if photo_id in existing_photo_ids:
                raise ValueError(f"photo id already exists: {photo_id}")

            spot_id = photo["spotId"]
            spot = plan_spots_by_id.get(spot_id)
            if spot is None:
                raise ValueError(f"spotId is not found in travel plan: {spot_id}")

            prompt = _build_image_analysis_prompt(
                travel_plan.destination,
                spot.name,
                photo.get("userDescription"),
            )
            analysis_data = await self._ai_service.analyze_image_structured(
                prompt=prompt,
                image_uri=photo["url"],
                response_schema=_IMAGE_ANALYSIS_SCHEMA,
                system_instruction=(
                    "レスポンススキーマに一致するJSONのみを返してください。"
                    "キー: detectedSpots, historicalElements, landmarks, confidence"
                ),
                temperature=0.0,
            )
            analysis = _parse_image_analysis_data(analysis_data, index=index)

            new_photos.append(
                Photo(
                    id=photo_id,
                    spot_id=spot_id,
                    url=photo["url"],
                    analysis=analysis,
                    user_description=photo.get("userDescription"),
                )
            )

        if existing_reflection is None:
            reflection = Reflection(
                plan_id=plan_id,
                user_id=user_id,
                photos=new_photos,
            )
            if spot_note_provided:
                reflection.update_spot_note(spot_id, spot_note)
            saved_reflection = self._reflection_repository.save(reflection)
        else:
            for photo in new_photos:
                existing_reflection.add_photo(photo)
            if spot_note_provided:
                existing_reflection.update_spot_note(spot_id, spot_note)
            saved_reflection = self._reflection_repository.save(existing_reflection)

        return ReflectionDTO.from_entity(saved_reflection)
