"""_generate_images_parallel()メソッドのユニットテスト"""

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest

from app.application.use_cases.generate_spot_images import GenerateSpotImagesUseCase
from app.domain.travel_guide.value_objects import SpotDetail


class TestGenerateImagesParallel:
    """_generate_images_parallel()メソッドのテストクラス"""

    @pytest.mark.asyncio
    async def test_generate_images_parallel_success(self) -> None:
        """複数スポットの画像を並列生成できる"""
        # Arrange
        mock_ai_service = Mock()
        mock_storage_service = Mock()
        mock_guide_repository = Mock()

        use_case = GenerateSpotImagesUseCase(
            ai_service=mock_ai_service,
            storage_service=mock_storage_service,
            guide_repository=mock_guide_repository,
            max_concurrent=2,
        )

        # _generate_single_spot_imageをモック化
        async def mock_generate_single(plan_id: str, spot: SpotDetail) -> tuple[str, str | None, str]:
            await asyncio.sleep(0.01)  # 非同期処理をシミュレート
            return (spot.spot_name, f"https://example.com/{spot.spot_name}.jpg", "succeeded")

        use_case._generate_single_spot_image = AsyncMock(side_effect=mock_generate_single)  # type: ignore

        spot_details = [
            SpotDetail(
                spot_name="金閣寺",
                historical_background="室町時代の寺院",
                highlights=("金箔の外観", "美しい庭園"),
                recommended_visit_time="午前中",
                historical_significance="世界遺産",
            ),
            SpotDetail(
                spot_name="清水寺",
                historical_background="平安時代の寺院",
                highlights=("清水の舞台", "音羽の滝"),
                recommended_visit_time="午後",
                historical_significance="世界遺産",
            ),
            SpotDetail(
                spot_name="伏見稲荷大社",
                historical_background="江戸時代の神社",
                highlights=("千本鳥居", "山頂からの眺望"),
                recommended_visit_time="早朝",
                historical_significance="重要文化財",
            ),
        ]

        # Act
        results = await use_case._generate_images_parallel("plan-123", spot_details)

        # Assert
        assert len(results) == 3
        assert all(status == "succeeded" for _, _, status in results)
        assert all(url is not None for _, url, _ in results)

        # すべてのスポットが処理されたことを確認
        spot_names = {name for name, _, _ in results}
        assert spot_names == {"金閣寺", "清水寺", "伏見稲荷大社"}

    @pytest.mark.asyncio
    async def test_generate_images_parallel_partial_failure(self) -> None:
        """一部のスポットが失敗しても成功した結果を返す"""
        # Arrange
        mock_ai_service = Mock()
        mock_storage_service = Mock()
        mock_guide_repository = Mock()

        use_case = GenerateSpotImagesUseCase(
            ai_service=mock_ai_service,
            storage_service=mock_storage_service,
            guide_repository=mock_guide_repository,
            max_concurrent=2,
        )

        # _generate_single_spot_imageをモック化（2番目のスポットは失敗）
        async def mock_generate_single(plan_id: str, spot: SpotDetail) -> tuple[str, str | None, str]:
            await asyncio.sleep(0.01)
            if spot.spot_name == "清水寺":
                return (spot.spot_name, None, "failed")
            return (spot.spot_name, f"https://example.com/{spot.spot_name}.jpg", "succeeded")

        use_case._generate_single_spot_image = AsyncMock(side_effect=mock_generate_single)  # type: ignore

        spot_details = [
            SpotDetail(
                spot_name="金閣寺",
                historical_background="室町時代の寺院",
                highlights=("金箔の外観",),
                recommended_visit_time="午前中",
                historical_significance="世界遺産",
            ),
            SpotDetail(
                spot_name="清水寺",
                historical_background="平安時代の寺院",
                highlights=("清水の舞台",),
                recommended_visit_time="午後",
                historical_significance="世界遺産",
            ),
            SpotDetail(
                spot_name="伏見稲荷大社",
                historical_background="江戸時代の神社",
                highlights=("千本鳥居",),
                recommended_visit_time="早朝",
                historical_significance="重要文化財",
            ),
        ]

        # Act
        results = await use_case._generate_images_parallel("plan-123", spot_details)

        # Assert
        assert len(results) == 3

        # 成功したスポットを確認
        succeeded = [(name, url) for name, url, status in results if status == "succeeded"]
        assert len(succeeded) == 2
        assert all(url is not None for _, url in succeeded)

        # 失敗したスポットを確認
        failed = [(name, url) for name, url, status in results if status == "failed"]
        assert len(failed) == 1
        assert failed[0][0] == "清水寺"
        assert failed[0][1] is None

    @pytest.mark.asyncio
    async def test_generate_images_parallel_respects_max_concurrent(self) -> None:
        """max_concurrentの制限が機能する"""
        # Arrange
        mock_ai_service = Mock()
        mock_storage_service = Mock()
        mock_guide_repository = Mock()

        use_case = GenerateSpotImagesUseCase(
            ai_service=mock_ai_service,
            storage_service=mock_storage_service,
            guide_repository=mock_guide_repository,
            max_concurrent=2,  # 最大2つまで同時実行
        )

        # 同時実行数を追跡
        concurrent_count = 0
        max_concurrent_observed = 0

        async def mock_generate_single(plan_id: str, spot: SpotDetail) -> tuple[str, str | None, str]:
            nonlocal concurrent_count, max_concurrent_observed
            concurrent_count += 1
            max_concurrent_observed = max(max_concurrent_observed, concurrent_count)
            await asyncio.sleep(0.05)  # 処理時間をシミュレート
            concurrent_count -= 1
            return (spot.spot_name, f"https://example.com/{spot.spot_name}.jpg", "succeeded")

        use_case._generate_single_spot_image = AsyncMock(side_effect=mock_generate_single)  # type: ignore

        spot_details = [
            SpotDetail(
                spot_name=f"スポット{i}",
                historical_background="テスト",
                highlights=("テスト",),
                recommended_visit_time="午前中",
                historical_significance="テスト",
            )
            for i in range(5)
        ]

        # Act
        results = await use_case._generate_images_parallel("plan-123", spot_details)

        # Assert
        assert len(results) == 5
        assert max_concurrent_observed <= 2  # 最大同時実行数が制限されている

    @pytest.mark.asyncio
    async def test_generate_images_parallel_empty_list(self) -> None:
        """空のスポットリストでも正常に動作する"""
        # Arrange
        mock_ai_service = Mock()
        mock_storage_service = Mock()
        mock_guide_repository = Mock()

        use_case = GenerateSpotImagesUseCase(
            ai_service=mock_ai_service,
            storage_service=mock_storage_service,
            guide_repository=mock_guide_repository,
        )

        # Act
        results = await use_case._generate_images_parallel("plan-123", [])

        # Assert
        assert results == []

