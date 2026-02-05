"""GenerateSpotImagesUseCaseのユニットテスト"""

import pytest

from app.application.use_cases.generate_spot_images import GenerateSpotImagesUseCase


class TestGenerateSpotImagesUseCase:
    """GenerateSpotImagesUseCaseのテストクラス"""

    def test_get_image_path_with_japanese_spot_name(self) -> None:
        """日本語のスポット名で画像パスを生成できる"""
        # Arrange
        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=None,  # type: ignore
        )
        plan_id = "plan-123"
        spot_name = "金閣寺"

        # Act
        path = use_case._get_image_path(plan_id, spot_name)

        # Assert
        assert path == "travel-guides/plan-123/spots/%E9%87%91%E9%96%A3%E5%AF%BA.jpg"

    def test_get_image_path_with_english_spot_name(self) -> None:
        """英語のスポット名（スペース含む）で画像パスを生成できる"""
        # Arrange
        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=None,  # type: ignore
        )
        plan_id = "plan-456"
        spot_name = "Eiffel Tower"

        # Act
        path = use_case._get_image_path(plan_id, spot_name)

        # Assert
        assert path == "travel-guides/plan-456/spots/Eiffel%20Tower.jpg"

    def test_get_image_path_with_special_characters(self) -> None:
        """特殊文字を含むスポット名で画像パスを生成できる"""
        # Arrange
        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=None,  # type: ignore
        )
        plan_id = "plan-789"
        spot_name = "St. Peter's Basilica"

        # Act
        path = use_case._get_image_path(plan_id, spot_name)

        # Assert
        # ピリオド、アポストロフィ、スペースがエンコードされる
        assert path == "travel-guides/plan-789/spots/St.%20Peter%27s%20Basilica.jpg"

    def test_get_image_path_format(self) -> None:
        """画像パスが正しい形式で生成される"""
        # Arrange
        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=None,  # type: ignore
        )
        plan_id = "test-plan"
        spot_name = "Test Spot"

        # Act
        path = use_case._get_image_path(plan_id, spot_name)

        # Assert
        assert path.startswith("travel-guides/")
        assert f"/{plan_id}/spots/" in path
        assert path.endswith(".jpg")

    def test_get_image_path_with_slash_in_spot_name(self) -> None:
        """スラッシュを含むスポット名で画像パスを生成できる"""
        # Arrange
        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=None,  # type: ignore
        )
        plan_id = "plan-999"
        spot_name = "Tokyo/Kyoto"

        # Act
        path = use_case._get_image_path(plan_id, spot_name)

        # Assert
        # スラッシュもエンコードされる（パス区切りと混同しないため）
        assert path == "travel-guides/plan-999/spots/Tokyo%2FKyoto.jpg"


class TestUpdateSpotImageStatus:
    """_update_spot_image_status()メソッドのテストクラス"""

    @pytest.mark.asyncio
    async def test_update_spot_image_status_success(self) -> None:
        """スポット画像ステータスを正常に更新できる"""
        # Arrange
        from unittest.mock import AsyncMock, MagicMock

        from app.domain.travel_guide.entity import TravelGuide
        from app.domain.travel_guide.value_objects import (
            Checkpoint,
            HistoricalEvent,
            SpotDetail,
        )

        # モックリポジトリを作成
        mock_repository = MagicMock()

        # テスト用のTravelGuideを作成
        spot_details = [
            SpotDetail(
                spot_name="金閣寺",
                historical_background="室町時代に建立された寺院",
                highlights=("金箔で覆われた外観", "美しい庭園"),
                recommended_visit_time="午前中",
                historical_significance="室町文化を代表する建築物",
                image_url=None,
                image_status="not_started",
            ),
            SpotDetail(
                spot_name="清水寺",
                historical_background="平安時代に建立された寺院",
                highlights=("清水の舞台", "音羽の滝"),
                recommended_visit_time="午後",
                historical_significance="京都を代表する寺院",
                image_url=None,
                image_status="not_started",
            ),
        ]

        travel_guide = TravelGuide(
            id="guide-123",
            plan_id="plan-123",
            overview="京都の歴史的な寺院を巡る旅",
            timeline=[
                HistoricalEvent(
                    year=1397,
                    event="金閣寺建立",
                    significance="室町文化の象徴",
                    related_spots=("金閣寺",),
                )
            ],
            spot_details=spot_details,
            checkpoints=[
                Checkpoint(
                    spot_name="金閣寺",
                    checkpoints=("入口", "庭園"),
                    historical_context="室町時代の建築",
                )
            ],
        )

        mock_repository.find_by_plan_id.return_value = travel_guide
        mock_repository.save.return_value = travel_guide

        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=mock_repository,
        )

        # Act
        await use_case._update_spot_image_status(
            plan_id="plan-123",
            spot_name="金閣寺",
            image_url="https://storage.googleapis.com/bucket/image.jpg",
            image_status="succeeded",
        )

        # Assert
        mock_repository.find_by_plan_id.assert_called_once_with("plan-123")
        mock_repository.save.assert_called_once()

        # 保存されたTravelGuideを確認
        saved_guide = mock_repository.save.call_args[0][0]
        updated_spot = next(s for s in saved_guide.spot_details if s.spot_name == "金閣寺")
        assert updated_spot.image_url == "https://storage.googleapis.com/bucket/image.jpg"
        assert updated_spot.image_status == "succeeded"

        # 他のスポットは変更されていないことを確認
        other_spot = next(s for s in saved_guide.spot_details if s.spot_name == "清水寺")
        assert other_spot.image_url is None
        assert other_spot.image_status == "not_started"

    @pytest.mark.asyncio
    async def test_update_spot_image_status_travel_guide_not_found(self) -> None:
        """TravelGuideが見つからない場合、エラーログを出力して正常終了する"""
        # Arrange
        from unittest.mock import MagicMock

        mock_repository = MagicMock()
        mock_repository.find_by_plan_id.return_value = None

        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=mock_repository,
        )

        # Act
        await use_case._update_spot_image_status(
            plan_id="non-existent-plan",
            spot_name="金閣寺",
            image_url="https://storage.googleapis.com/bucket/image.jpg",
            image_status="succeeded",
        )

        # Assert
        mock_repository.find_by_plan_id.assert_called_once_with("non-existent-plan")
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_spot_image_status_spot_not_found(self) -> None:
        """該当スポットが見つからない場合、警告ログを出力して正常終了する"""
        # Arrange
        from unittest.mock import MagicMock

        from app.domain.travel_guide.entity import TravelGuide
        from app.domain.travel_guide.value_objects import (
            Checkpoint,
            HistoricalEvent,
            SpotDetail,
        )

        mock_repository = MagicMock()

        travel_guide = TravelGuide(
            id="guide-123",
            plan_id="plan-123",
            overview="京都の歴史的な寺院を巡る旅",
            timeline=[
                HistoricalEvent(
                    year=1397,
                    event="金閣寺建立",
                    significance="室町文化の象徴",
                    related_spots=("金閣寺",),
                )
            ],
            spot_details=[
                SpotDetail(
                    spot_name="金閣寺",
                    historical_background="室町時代に建立された寺院",
                    highlights=("金箔で覆われた外観", "美しい庭園"),
                    recommended_visit_time="午前中",
                    historical_significance="室町文化を代表する建築物",
                )
            ],
            checkpoints=[
                Checkpoint(
                    spot_name="金閣寺",
                    checkpoints=("入口", "庭園"),
                    historical_context="室町時代の建築",
                )
            ],
        )

        mock_repository.find_by_plan_id.return_value = travel_guide

        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=mock_repository,
        )

        # Act
        await use_case._update_spot_image_status(
            plan_id="plan-123",
            spot_name="存在しないスポット",
            image_url="https://storage.googleapis.com/bucket/image.jpg",
            image_status="succeeded",
        )

        # Assert
        mock_repository.find_by_plan_id.assert_called_once_with("plan-123")
        mock_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_spot_image_status_with_failed_status(self) -> None:
        """失敗ステータス（image_url=None）で更新できる"""
        # Arrange
        from unittest.mock import MagicMock

        from app.domain.travel_guide.entity import TravelGuide
        from app.domain.travel_guide.value_objects import (
            Checkpoint,
            HistoricalEvent,
            SpotDetail,
        )

        mock_repository = MagicMock()

        travel_guide = TravelGuide(
            id="guide-123",
            plan_id="plan-123",
            overview="京都の歴史的な寺院を巡る旅",
            timeline=[
                HistoricalEvent(
                    year=1397,
                    event="金閣寺建立",
                    significance="室町文化の象徴",
                    related_spots=("金閣寺",),
                )
            ],
            spot_details=[
                SpotDetail(
                    spot_name="金閣寺",
                    historical_background="室町時代に建立された寺院",
                    highlights=("金箔で覆われた外観", "美しい庭園"),
                    recommended_visit_time="午前中",
                    historical_significance="室町文化を代表する建築物",
                    image_status="processing",
                )
            ],
            checkpoints=[
                Checkpoint(
                    spot_name="金閣寺",
                    checkpoints=("入口", "庭園"),
                    historical_context="室町時代の建築",
                )
            ],
        )

        mock_repository.find_by_plan_id.return_value = travel_guide
        mock_repository.save.return_value = travel_guide

        use_case = GenerateSpotImagesUseCase(
            ai_service=None,  # type: ignore
            storage_service=None,  # type: ignore
            guide_repository=mock_repository,
        )

        # Act
        await use_case._update_spot_image_status(
            plan_id="plan-123",
            spot_name="金閣寺",
            image_url=None,
            image_status="failed",
        )

        # Assert
        saved_guide = mock_repository.save.call_args[0][0]
        updated_spot = saved_guide.spot_details[0]
        assert updated_spot.image_url is None
        assert updated_spot.image_status == "failed"


class TestExecuteMethod:
    """execute()メソッドのテストクラス"""

    @pytest.mark.asyncio
    async def test_execute_calls_parallel_generation_and_updates_db(self) -> None:
        """execute()が並列処理を呼び出し、各スポットのDB更新を行う"""
        # Arrange
        from unittest.mock import AsyncMock, MagicMock

        from app.domain.travel_guide.entity import TravelGuide
        from app.domain.travel_guide.value_objects import Checkpoint, HistoricalEvent, SpotDetail

        mock_ai_service = MagicMock()
        mock_storage_service = MagicMock()
        mock_repository = MagicMock()

        spot_details = [
            SpotDetail(
                spot_name="金閣寺",
                historical_background="室町時代に建立された寺院",
                highlights=("金箔で覆われた外観", "美しい庭園"),
                recommended_visit_time="午前中",
                historical_significance="室町文化を代表する建築物",
            ),
            SpotDetail(
                spot_name="清水寺",
                historical_background="平安時代に建立された寺院",
                highlights=("清水の舞台", "音羽の滝"),
                recommended_visit_time="午後",
                historical_significance="京都を代表する寺院",
            ),
            SpotDetail(
                spot_name="伏見稲荷大社",
                historical_background="千本鳥居で有名な神社",
                highlights=("千本鳥居", "山頂からの眺望"),
                recommended_visit_time="午前中",
                historical_significance="稲荷信仰の総本社",
            ),
        ]

        # モックの旅行ガイドを作成
        mock_guide = TravelGuide(
            id="guide-123",
            plan_id="plan-123",
            overview="京都の主要な観光スポットを巡る旅行ガイド",
            timeline=[
                HistoricalEvent(
                    year=1397,
                    event="金閣寺創建",
                    significance="室町文化の象徴",
                    related_spots=("金閣寺",),
                ),
            ],
            spot_details=spot_details,
            checkpoints=[
                Checkpoint(
                    spot_name="金閣寺",
                    checkpoints=("金箔の舎利殿を観察",),
                    historical_context="室町文化の象徴",
                ),
            ],
        )

        # リポジトリのモック設定
        mock_repository.find_by_plan_id.return_value = mock_guide

        use_case = GenerateSpotImagesUseCase(
            ai_service=mock_ai_service,
            storage_service=mock_storage_service,
            guide_repository=mock_repository,
            max_concurrent=3,
        )

        # _generate_images_parallelをモック化
        use_case._generate_images_parallel = AsyncMock(
            return_value=[
                ("金閣寺", "https://storage.googleapis.com/bucket/image1.jpg", "succeeded"),
                ("清水寺", "https://storage.googleapis.com/bucket/image2.jpg", "succeeded"),
                ("伏見稲荷大社", None, "failed"),
            ]
        )

        # _update_spot_image_statusをモック化
        use_case._update_spot_image_status = AsyncMock()

        # Act
        await use_case.execute(plan_id="plan-123")

        # Assert
        # リポジトリから旅行ガイドを取得したことを確認
        mock_repository.find_by_plan_id.assert_called_once_with("plan-123")

        # 並列処理が呼び出されたことを確認
        use_case._generate_images_parallel.assert_called_once_with("plan-123", spot_details)

        # 各スポットのDB更新が呼び出されたことを確認
        assert use_case._update_spot_image_status.call_count == 3

        # 各呼び出しの引数を確認
        calls = use_case._update_spot_image_status.call_args_list
        assert calls[0].kwargs == {
            "plan_id": "plan-123",
            "spot_name": "金閣寺",
            "image_url": "https://storage.googleapis.com/bucket/image1.jpg",
            "image_status": "succeeded",
        }
        assert calls[1].kwargs == {
            "plan_id": "plan-123",
            "spot_name": "清水寺",
            "image_url": "https://storage.googleapis.com/bucket/image2.jpg",
            "image_status": "succeeded",
        }
        assert calls[2].kwargs == {
            "plan_id": "plan-123",
            "spot_name": "伏見稲荷大社",
            "image_url": None,
            "image_status": "failed",
        }

    @pytest.mark.asyncio
    async def test_execute_with_guide_not_found(self) -> None:
        """旅行ガイドが見つからない場合は警告ログを出力して終了する"""
        # Arrange
        from unittest.mock import AsyncMock, MagicMock

        mock_ai_service = MagicMock()
        mock_storage_service = MagicMock()
        mock_repository = MagicMock()

        # 旅行ガイドが見つからない場合
        mock_repository.find_by_plan_id.return_value = None

        use_case = GenerateSpotImagesUseCase(
            ai_service=mock_ai_service,
            storage_service=mock_storage_service,
            guide_repository=mock_repository,
        )

        use_case._generate_images_parallel = AsyncMock(return_value=[])
        use_case._update_spot_image_status = AsyncMock()

        # Act
        await use_case.execute(plan_id="plan-123")

        # Assert
        mock_repository.find_by_plan_id.assert_called_once_with("plan-123")
        use_case._generate_images_parallel.assert_not_called()
        use_case._update_spot_image_status.assert_not_called()
