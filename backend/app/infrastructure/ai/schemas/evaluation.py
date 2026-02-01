"""旅行ガイド評価用のスキーマ定義"""

from __future__ import annotations

from pydantic import Field

from app.infrastructure.ai.schemas.base import GeminiResponseSchema


class SpotEvaluation(GeminiResponseSchema):
    """スポット評価結果"""

    spot_name: str = Field(
        ...,
        description="スポット名",
        alias="spotName",
    )
    has_citation: bool = Field(
        ...,
        description="出典が含まれているか（URL、書籍名、施設の展示、公式サイト、公的機関の資料など）",
        alias="hasCitation",
    )
    citation_example: str = Field(
        ...,
        description="見つかった出典の例（見つからない場合は空文字列）",
        alias="citationExample",
    )


class TravelGuideEvaluationSchema(GeminiResponseSchema):
    """旅行ガイド評価結果のスキーマ"""

    spot_evaluations: list[SpotEvaluation] = Field(
        ...,
        description="各スポットの評価結果",
        alias="spotEvaluations",
    )
    has_historical_comparison: bool = Field(
        ...,
        description="overviewに歴史の有名な話題との対比が含まれているか（例: 同時期の世界では、一方ヨーロッパでは、など）",
        alias="hasHistoricalComparison",
    )
    historical_comparison_example: str = Field(
        ...,
        description="見つかった歴史的対比の例（見つからない場合は空文字列）",
        alias="historicalComparisonExample",
    )
