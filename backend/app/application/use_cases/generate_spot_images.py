"""スポット画像生成ユースケース"""

import asyncio
import logging
from urllib.parse import quote

import filetype

from app.application.ports.ai_service import IAIService
from app.application.ports.storage_service import IStorageService
from app.domain.travel_guide.repository import ITravelGuideRepository
from app.domain.travel_guide.value_objects import SpotDetail

logger = logging.getLogger(__name__)


class GenerateSpotImagesUseCase:
    """スポット画像生成ユースケース"""

    def __init__(
        self,
        ai_service: IAIService,
        storage_service: IStorageService,
        guide_repository: ITravelGuideRepository,
        max_concurrent: int = 3,
    ) -> None:
        """初期化

        Args:
            ai_service: AIサービス
            storage_service: ストレージサービス
            guide_repository: 旅行ガイドリポジトリ
            max_concurrent: 最大同時実行数
        """
        self._ai_service = ai_service
        self._storage_service = storage_service
        self._guide_repository = guide_repository
        self._max_concurrent = max_concurrent

    def _get_image_path(self, plan_id: str, spot_name: str, extension: str = "jpg") -> str:
        """画像保存パスを生成する

        Args:
            plan_id: 旅行計画ID
            spot_name: スポット名
            extension: 画像拡張子（例: "jpg", "png", "webp"）

        Returns:
            str: 画像保存パス（例: travel-guides/{plan_id}/spots/{spot_name_safe}.jpg）

        Note:
            スポット名はurllib.parse.quoteを使用してURLセーフに変換されます。
            例: "金閣寺" → "%E9%87%91%E9%96%A3%E5%AF%BA"
            例: "Eiffel Tower" → "Eiffel%20Tower"
        """
        # スポット名をURLセーフに変換（safe=''で全ての特殊文字をエンコード）
        spot_name_safe = quote(spot_name, safe="")
        return f"travel-guides/{plan_id}/spots/{spot_name_safe}.{extension}"

    def _detect_image_format(self, image_data: bytes) -> tuple[str, str]:
        """画像データから拡張子とMIMEタイプを判定する

        Args:
            image_data: 画像データ

        Returns:
            tuple[str, str]: (拡張子, MIMEタイプ)
        """
        kind = filetype.guess(image_data[:261])
        if kind is None:
            raise ValueError("image format could not be detected.")

        extension = kind.extension
        mime_type = kind.mime

        allowed = {"jpg", "jpeg", "png", "webp"}
        if extension not in allowed:
            raise ValueError(f"unsupported image format: {extension}")

        if extension in {"jpg", "jpeg"}:
            return ("jpg", "image/jpeg")

        return (extension, mime_type)

    async def execute(
        self,
        plan_id: str,
    ) -> None:
        """スポット画像を生成する

        Args:
            plan_id: 旅行計画ID

        Note:
            このメソッドは非同期で実行され、呼び出し元は完了を待たない
            各スポットの画像生成完了後、個別にDBを更新する

            DBから最新の旅行ガイドを取得し、全てのスポット（既存+新規）に対して
            画像生成を実行します。
        """
        # DBから最新の旅行ガイドを取得
        travel_guide = self._guide_repository.find_by_plan_id(plan_id)
        if travel_guide is None:
            logger.warning(
                "Travel guide not found for image generation",
                extra={"plan_id": plan_id},
            )
            return

        spot_details = travel_guide.spot_details

        logger.info(
            "Starting spot images generation",
            extra={
                "plan_id": plan_id,
                "total_spots": len(spot_details),
            },
        )

        # 並列処理で画像を生成
        results = await self._generate_images_parallel(plan_id, spot_details)

        # 各スポットの結果を個別にDB更新
        for spot_name, image_url, image_status, _ in results:
            await self._update_spot_image_status(
                plan_id=plan_id,
                spot_name=spot_name,
                image_url=image_url,
                image_status=image_status,
            )

        logger.info(
            "Completed spot images generation",
            extra={
                "plan_id": plan_id,
                "total_spots": len(spot_details),
                "succeeded": sum(1 for _, _, status, _ in results if status == "succeeded"),
                "failed": sum(1 for _, _, status, _ in results if status == "failed"),
            },
        )

    async def generate_for_spot(
        self,
        plan_id: str,
        spot_name: str,
    ) -> tuple[str | None, str, str | None]:
        """単一スポットの画像生成を実行する

        Args:
            plan_id: 旅行計画ID
            spot_name: スポット名

        Returns:
            tuple[str | None, str, str | None]: (画像URL, ステータス, エラーメッセージ)
        """
        travel_guide = self._guide_repository.find_by_plan_id(plan_id)
        if travel_guide is None:
            logger.error(
                "Travel guide not found for spot image generation",
                extra={"plan_id": plan_id, "spot_name": spot_name},
            )
            return (None, "failed", "Travel guide not found")

        spot_detail = next(
            (detail for detail in travel_guide.spot_details if detail.spot_name == spot_name),
            None,
        )
        if spot_detail is None:
            logger.error(
                "Spot not found in travel guide for image generation",
                extra={"plan_id": plan_id, "spot_name": spot_name},
            )
            return (None, "failed", "Spot not found in travel guide")

        await self._update_spot_image_status(
            plan_id=plan_id,
            spot_name=spot_name,
            image_url=None,
            image_status="processing",
        )

        _, image_url, status, error_message = await self._generate_single_spot_image(
            plan_id, spot_detail
        )

        await self._update_spot_image_status(
            plan_id=plan_id,
            spot_name=spot_name,
            image_url=image_url,
            image_status=status,
        )

        return (image_url, status, error_message)

    async def _upload_and_get_url(
        self,
        image_data: bytes,
        plan_id: str,
        spot_name: str,
    ) -> str:
        """画像をアップロードして署名付きURLを取得する

        Args:
            image_data: 画像データ（JPEG形式）
            plan_id: 旅行計画ID
            spot_name: スポット名

        Returns:
            str: 署名付きURL（7日間有効）

        Raises:
            StorageOperationError: アップロード失敗
        """
        extension, content_type = self._detect_image_format(image_data)
        path = self._get_image_path(plan_id, spot_name, extension)
        # CloudStorageService.upload_file()は署名付きURLを返す
        signed_url = await self._storage_service.upload_file(
            file_data=image_data,
            destination=path,
            content_type=content_type,
        )
        return signed_url

    async def _generate_single_spot_image(
        self,
        plan_id: str,
        spot_detail: SpotDetail,
    ) -> tuple[str, str | None, str, str | None]:
        """単一スポットの画像を生成する

        Args:
            plan_id: 旅行計画ID
            spot_detail: スポット詳細

        Returns:
            tuple[str, str | None, str, str | None]: (スポット名, 画像URL or None, ステータス, エラーメッセージ)

        Note:
            プロンプト生成→画像生成→アップロードの流れで処理します。
            エラーが発生した場合は、適切なログを出力し、失敗ステータスを返します。
        """
        spot_name = spot_detail.spot_name

        try:
            logger.info(
                "Starting image generation for spot",
                extra={"plan_id": plan_id, "spot_name": spot_name},
            )

            # ステップ1: プロンプト生成（Gemini API使用）
            try:
                prompt = await self._ai_service.generate_image_prompt(
                    spot_name=spot_name,
                    historical_background=spot_detail.historical_background,
                )
                logger.debug(
                    "Generated image prompt",
                    extra={
                        "plan_id": plan_id,
                        "spot_name": spot_name,
                        "prompt_length": len(prompt),
                    },
                )
            except Exception as e:
                logger.error(
                    "Failed to generate image prompt",
                    extra={
                        "plan_id": plan_id,
                        "spot_name": spot_name,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                return (spot_name, None, "failed", f"prompt generation failed: {e}")

            # ステップ2: 画像生成（Vertex AI Image Generation API使用）
            try:
                image_data = await self._ai_service.generate_image(
                    prompt=prompt,
                    aspect_ratio="16:9",
                    timeout=60,
                )
                logger.debug(
                    "Generated image",
                    extra={
                        "plan_id": plan_id,
                        "spot_name": spot_name,
                        "image_size_bytes": len(image_data),
                    },
                )
            except Exception as e:
                logger.error(
                    "Failed to generate image",
                    extra={
                        "plan_id": plan_id,
                        "spot_name": spot_name,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                return (spot_name, None, "failed", f"image generation failed: {e}")

            # ステップ3: 画像アップロード（Cloud Storage）
            try:
                image_url = await self._upload_and_get_url(
                    image_data=image_data,
                    plan_id=plan_id,
                    spot_name=spot_name,
                )
                logger.info(
                    "Successfully uploaded image",
                    extra={
                        "plan_id": plan_id,
                        "spot_name": spot_name,
                        "image_url_length": len(image_url),
                    },
                )
                return (spot_name, image_url, "succeeded", None)
            except Exception as e:
                logger.error(
                    "Failed to upload image to Cloud Storage",
                    extra={
                        "plan_id": plan_id,
                        "spot_name": spot_name,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                return (spot_name, None, "failed", f"upload failed: {e}")

        except Exception as e:
            # 予期しないエラーをキャッチ
            logger.error(
                "Unexpected error during image generation",
                extra={
                    "plan_id": plan_id,
                    "spot_name": spot_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            return (spot_name, None, "failed", f"unexpected error: {e}")

    async def _generate_images_parallel(
        self,
        plan_id: str,
        spot_details: list[SpotDetail],
    ) -> list[tuple[str, str | None, str, str | None]]:
        """複数スポットの画像を並列生成する

        Args:
            plan_id: 旅行計画ID
            spot_details: スポット詳細リスト

        Returns:
            list[tuple[str, str | None, str, str | None]]: (スポット名, 画像URL or None, ステータス, エラーメッセージ)のリスト

        Note:
            - asyncio.Semaphoreで並行実行数を制限します（デフォルト: 3）
            - asyncio.gatherで並列実行します
            - 一部のタスクが失敗しても、成功したタスクの結果を返します
            - 各タスクは例外をキャッチして失敗ステータスを返すため、gatherは例外を発生させません
        """
        # 並行実行数を制限するセマフォ
        semaphore = asyncio.Semaphore(self._max_concurrent)

        async def _generate_with_semaphore(
            spot: SpotDetail,
        ) -> tuple[str, str | None, str, str | None]:
            """セマフォを使用して並行実行数を制限しながら画像を生成する"""
            async with semaphore:
                try:
                    return await self._generate_single_spot_image(plan_id, spot)
                except Exception as e:
                    # _generate_single_spot_imageは既に例外をキャッチしているが、
                    # 念のため追加のエラーハンドリングを行う
                    logger.error(
                        "Image generation failed for spot",
                        extra={
                            "plan_id": plan_id,
                            "spot_name": spot.spot_name,
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                        },
                        exc_info=True,
                    )
                    # 失敗した場合もステータスを返す
                    return (spot.spot_name, None, "failed", f"unexpected error: {e}")

        # すべてのスポットに対してタスクを作成
        tasks = [_generate_with_semaphore(spot) for spot in spot_details]

        # 並列実行（return_exceptions=Falseだが、各タスクが例外をキャッチするため問題なし）
        results = await asyncio.gather(*tasks, return_exceptions=False)

        logger.info(
            "Completed parallel image generation",
            extra={
                "plan_id": plan_id,
                "total_spots": len(spot_details),
                "succeeded": sum(1 for _, _, status, _ in results if status == "succeeded"),
                "failed": sum(1 for _, _, status, _ in results if status == "failed"),
            },
        )

        return results

    async def _update_spot_image_status(
        self,
        plan_id: str,
        spot_name: str,
        image_url: str | None,
        image_status: str,
    ) -> None:
        """スポットの画像ステータスを更新する

        Args:
            plan_id: 旅行計画ID
            spot_name: スポット名
            image_url: 画像URL（失敗時はNone）
            image_status: 画像生成ステータス

        Note:
            TravelGuideを取得し、該当スポットのSpotDetailを更新して保存する
        """
        try:
            self._guide_repository.update_spot_image_status(
                plan_id=plan_id,
                spot_name=spot_name,
                image_url=image_url,
                image_status=image_status,
                commit=True,
            )
            logger.info(
                "Successfully updated spot image status in database",
                extra={
                    "plan_id": plan_id,
                    "spot_name": spot_name,
                    "image_status": image_status,
                },
            )

        except Exception as e:
            logger.error(
                "Failed to update spot image status in database",
                extra={
                    "plan_id": plan_id,
                    "spot_name": spot_name,
                    "image_status": image_status,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
