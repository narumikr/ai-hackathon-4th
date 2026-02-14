"""写真分析ユースケース"""

import asyncio
import logging

from app.application.dto.reflection_dto import ReflectionDTO
from app.application.ports.ai_service import IAIService
from app.application.use_cases.travel_plan_helpers import validate_required_str
from app.domain.reflection.entity import Photo, Reflection
from app.domain.reflection.repository import IReflectionRepository
from app.domain.reflection.value_objects import ImageAnalysis
from app.domain.travel_plan.exceptions import TravelPlanNotFoundError
from app.domain.travel_plan.repository import ITravelPlanRepository
from app.prompts import render_template

logger = logging.getLogger(__name__)


def _require_str(value: object, field_name: str) -> str:
    """必須の文字列フィールドを検証する"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} is required and must be a non-empty string.")
    return value.strip()


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


_IMAGE_ANALYSIS_PROMPT_TEMPLATE = "image_analysis_prompt.txt"
_IMAGE_ANALYSIS_SYSTEM_INSTRUCTION_TEMPLATE = "image_analysis_system_instruction.txt"
_MAX_CONCURRENT_IMAGE_ANALYSIS = 3
_MAX_IMAGE_ANALYSIS_RETRIES = 2
_RETRY_BASE_DELAY_SECONDS = 0.3


def _parse_image_analysis(response: str, *, index: int) -> ImageAnalysis:
    """AIの画像分析レスポンスをパースする"""
    if not response or not response.strip():
        raise ValueError(f"photos[{index}].analysis response must be a non-empty string.")

    return ImageAnalysis(description=response)


def _build_image_analysis_prompt(
    destination: str,
    spot_name: str,
    user_description: str | None,
) -> str:
    """画像分析のプロンプトを生成する"""
    description_text = ""
    if user_description:
        description_text = f"ユーザーの補足説明: {user_description}\n"
    return render_template(
        _IMAGE_ANALYSIS_PROMPT_TEMPLATE,
        destination=destination,
        spot_name=spot_name,
        description_text=description_text,
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
    ) -> ReflectionDTO | None:
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
        analysis_inputs: list[dict] = []
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
            analysis_inputs.append(
                {
                    "index": index,
                    "photo_id": photo_id,
                    "spot_id": spot_id,
                    "url": photo["url"],
                    "user_description": photo.get("userDescription"),
                    "prompt": prompt,
                }
            )

        semaphore = asyncio.Semaphore(_MAX_CONCURRENT_IMAGE_ANALYSIS)

        async def _analyze_single_photo(payload: dict) -> Photo | None:
            async with semaphore:
                last_error: Exception | None = None
                for attempt in range(_MAX_IMAGE_ANALYSIS_RETRIES + 1):
                    try:
                        analysis_text = await self._ai_service.analyze_image(
                            prompt=payload["prompt"],
                            image_uri=payload["url"],
                            system_instruction=render_template(
                                _IMAGE_ANALYSIS_SYSTEM_INSTRUCTION_TEMPLATE
                            ),
                            temperature=0.0,
                        )
                        analysis = _parse_image_analysis(analysis_text, index=payload["index"])
                        return Photo(
                            id=payload["photo_id"],
                            spot_id=payload["spot_id"],
                            url=payload["url"],
                            analysis=analysis,
                            user_description=payload["user_description"],
                        )
                    except Exception as exc:
                        last_error = exc
                        is_final_attempt = attempt >= _MAX_IMAGE_ANALYSIS_RETRIES
                        logger.warning(
                            "Image analysis attempt failed.",
                            exc_info=exc,
                            extra={
                                "plan_id": plan_id,
                                "photo_id": payload["photo_id"],
                                "spot_id": payload["spot_id"],
                                "attempt": attempt + 1,
                                "max_attempts": _MAX_IMAGE_ANALYSIS_RETRIES + 1,
                                "is_final_attempt": is_final_attempt,
                            },
                        )
                        if is_final_attempt:
                            break
                        await asyncio.sleep(_RETRY_BASE_DELAY_SECONDS * (2**attempt))

                logger.error(
                    "Image analysis failed after retries; skipping photo.",
                    exc_info=last_error,
                    extra={
                        "plan_id": plan_id,
                        "photo_id": payload["photo_id"],
                        "spot_id": payload["spot_id"],
                        "max_attempts": _MAX_IMAGE_ANALYSIS_RETRIES + 1,
                    },
                )
                return None

        tasks = [_analyze_single_photo(payload) for payload in analysis_inputs]
        results = await asyncio.gather(*tasks)
        new_photos = [photo for photo in results if photo is not None]
        failed_photo_count = len(analysis_inputs) - len(new_photos)
        if failed_photo_count > 0:
            logger.warning(
                "Some photo analyses failed and were skipped.",
                extra={
                    "plan_id": plan_id,
                    "user_id": user_id,
                    "requested_photo_count": len(analysis_inputs),
                    "successful_photo_count": len(new_photos),
                    "failed_photo_count": failed_photo_count,
                    "spot_id": spot_id,
                },
            )

        if not new_photos:
            if existing_reflection is None:
                logger.warning(
                    "No analyzable photos were produced and no reflection exists; skipping save.",
                    extra={
                        "plan_id": plan_id,
                        "user_id": user_id,
                        "requested_photo_count": len(analysis_inputs),
                        "spot_id": spot_id,
                    },
                )
                return None

            if spot_note_provided:
                existing_reflection.update_spot_note(spot_id, spot_note)
                self._reflection_repository.save(existing_reflection)
            return ReflectionDTO.from_entity(existing_reflection)

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
