"""AI統合のプロパティテスト

Property 2: Web search execution
Property 6: Historical background summarization
Property 7: Historical highlights organization

注意: これらのテストは外部API（Gemini API）をモック化しているため、
アダプタが正しい引数でクライアントを呼び出すことを検証します。
AIの実際の出力品質や振る舞いは検証していません。
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.domain.travel_guide.value_objects import SpotDetail
from app.infrastructure.ai.adapters import GeminiAIService
from app.infrastructure.ai.gemini_client import GeminiClient

# --- Hypothesisカスタム戦略定義 ---

MIN_HISTORICAL_BACKGROUND_LENGTH = 10
"""historical_backgroundの最小文字数

汎用的すぎる応答（「不明」「なし」など）を排除するための閾値。
10文字未満の歴史的背景は実質的な情報を含まないと判断する。
"""


def _non_empty_printable_text(min_size: int = 1, max_size: int = 50) -> st.SearchStrategy[str]:
    """非空のprintable文字列を生成するStrategy

    Hypothesis Strategy: テストデータ生成の設計図

    バリデーション要件に適合:
    - 空文字列は拒否される
    - 空白のみの文字列も拒否される。

    Args:
        min_size: 最小文字数
        max_size: 最大文字数

    Returns:
        ASCII 32-126 (printable文字: 画面表示可能な文字) の文字列Strategy
    """
    # ASCII 32-126: スペースから~までのprintable文字のみ
    # 制御文字（改行・タブなど）や拡張ASCII文字を排除し、安定したテストデータを生成
    return st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=min_size,
        max_size=max_size,
    ).filter(lambda value: value.strip() != "")  # 空白のみの文字列を除外


@st.composite
def _travel_destination_inputs(draw: st.DrawFn) -> tuple[str, str | None]:
    """旅行先入力データを生成するStrategy

    Hypothesis Composite Strategy: 複数の値を組み合わせて複雑なデータ構造を生成

    Property 2 (Web search execution) のテストデータ生成:
    - prompt: 旅行先に関する歴史情報リクエスト
    - system_instruction: オプショナルなシステム命令

    Args:
        draw: Hypothesisの描画関数

    Returns:
        (prompt, system_instruction)のタプル
    """
    # 旅行先プロンプト（例：「京都の歴史情報を教えて」）
    destination = draw(_non_empty_printable_text(max_size=80))
    prompt = f"Provide historical information about {destination}"

    # オプショナルなシステム命令
    system_instruction = draw(st.one_of(st.none(), _non_empty_printable_text(max_size=120)))

    return prompt, system_instruction


@st.composite
def _spot_info_inputs(draw: st.DrawFn) -> tuple[str, dict[str, Any]]:
    """観光スポット情報入力を生成するStrategy

    Hypothesis Composite Strategy: 複数の値を組み合わせて複雑なデータ構造を生成

    Property 6, 7 (Historical background summarization, Historical highlights organization) のテストデータ生成:
    - prompt: 観光スポットの詳細情報生成リクエスト
    - response_schema: SpotDetailのJSONスキーマ

    Args:
        draw: Hypothesisの描画関数

    Returns:
        (prompt, response_schema)のタプル
    """
    # 観光スポット名
    spot_name = draw(_non_empty_printable_text(max_size=80))
    prompt = f"Generate detailed historical information for {spot_name}"

    # SpotDetailのJSONスキーマ
    response_schema = {
        "type": "object",
        "properties": {
            "spot_name": {"type": "string"},
            "historical_background": {"type": "string"},
            "highlights": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
            },
            "recommended_visit_time": {"type": "string"},
            "historical_significance": {"type": "string"},
        },
        "required": [
            "spot_name",
            "historical_background",
            "highlights",
            "recommended_visit_time",
            "historical_significance",
        ],
    }

    return prompt, response_schema


# --- Property 2: Web search execution ---


@pytest.mark.asyncio
@given(inputs=_travel_destination_inputs())
@settings(max_examples=100)  # 最低100回実行
async def test_property_web_search_execution(inputs: tuple[str, str | None]) -> None:
    """Property 2: Web search executionを検証する

    前提条件:
    - 任意の旅行先入力が生成される
    - system_instructionはNoneまたは非空文字列

    検証項目:
    - GeminiAIService.generate_with_search()がGoogle Searchツールを使用してテキストを生成すること
    - GeminiClient.generate_content()がtools=["google_search"]で呼び出されること
    - 検索結果を含むテキストが返されること
    - 空文字列が返されないこと
    """
    prompt, system_instruction = inputs

    # モックGeminiClientの準備
    mock_client = MagicMock(spec=GeminiClient)
    expected_response = "Historical information with search results about the destination."
    mock_client.generate_content = AsyncMock(return_value=expected_response)

    # GeminiAIServiceのインスタンス作成
    service = GeminiAIService(
        gemini_client=mock_client,
        default_temperature=0.0,
        default_max_output_tokens=8192,
        default_timeout_seconds=60,
    )

    # 実行: Web検索統合でテキスト生成
    result = await service.generate_with_search(
        prompt=prompt,
        system_instruction=system_instruction,
    )

    # 検証1: GeminiClient.generate_content()がtools=["google_search"]で呼び出されること
    mock_client.generate_content.assert_called_once()
    call_kwargs = mock_client.generate_content.call_args.kwargs
    assert call_kwargs["tools"] == ["google_search"]
    assert call_kwargs["prompt"] == prompt
    assert call_kwargs["system_instruction"] == system_instruction

    # 検証2: デフォルトtemperature=0.0が使用されること（Function Calling推奨値）
    assert call_kwargs["temperature"] == 0.0

    # 検証3: 検索結果を含むテキストが返されること
    assert result == expected_response

    # 検証4: 空文字列が返されないこと
    assert result.strip() != ""


# --- Property 6: Historical background summarization ---


@pytest.mark.asyncio
@given(inputs=_spot_info_inputs())
@settings(max_examples=100)
async def test_property_historical_background_summarization(
    inputs: tuple[str, dict[str, Any]],
) -> None:
    """Property 6: Historical background summarizationを検証する

    前提条件:
    - 任意の観光スポット情報入力が生成される
    - 構造化データ生成のためのresponse_schemaが定義されている

    検証項目:
    - GeminiAIService.generate_structured_data()が構造化データを生成すること
    - GeminiClient.generate_content_with_schema()が正しいスキーマとtemperature=0.0で呼び出されること
    - SpotDetailが正しく生成されること
    - historical_backgroundフィールドが非空文字列であること
    - historical_backgroundが最小限の長さを持つこと（汎用的すぎる応答を排除）
    """
    prompt, response_schema = inputs

    # モックGeminiClientの準備
    mock_client = MagicMock(spec=GeminiClient)
    mock_spot_data = {
        "spot_name": "Historical Temple",
        "historical_background": "This temple was built in 778 AD and has a rich history.",
        "highlights": ["Main Hall", "Garden", "Stone Pagoda"],
        "recommended_visit_time": "Early morning",
        "historical_significance": "Important cultural heritage site",
    }
    mock_client.generate_content_with_schema = AsyncMock(return_value=mock_spot_data)

    # GeminiAIServiceのインスタンス作成
    service = GeminiAIService(
        gemini_client=mock_client,
        default_temperature=0.0,
        default_max_output_tokens=8192,
        default_timeout_seconds=60,
    )

    # 実行: 構造化データ生成
    result = await service.generate_structured_data(
        prompt=prompt,
        response_schema=response_schema,
    )

    # 検証1: GeminiClient.generate_content_with_schema()が適切に呼び出されること
    mock_client.generate_content_with_schema.assert_called_once()
    call_kwargs = mock_client.generate_content_with_schema.call_args.kwargs
    assert call_kwargs["prompt"] == prompt
    assert call_kwargs["response_schema"] == response_schema

    # 検証2: デフォルトtemperature=0.0が使用されること（構造化出力推奨値）
    assert call_kwargs["temperature"] == 0.0

    # 検証3: 構造化データが返されること
    assert isinstance(result, dict)
    assert "historical_background" in result

    # 検証4: SpotDetailが正しく生成できること
    spot_detail = SpotDetail(
        spot_name=result["spot_name"],
        historical_background=result["historical_background"],
        highlights=tuple(result["highlights"]),
        recommended_visit_time=result["recommended_visit_time"],
        historical_significance=result["historical_significance"],
    )

    # 検証5: historical_backgroundが非空文字列であること
    assert spot_detail.historical_background
    assert spot_detail.historical_background.strip() != ""

    # 検証6: historical_backgroundが最小限の長さを持つこと（汎用的すぎる応答を排除）
    assert len(spot_detail.historical_background) >= MIN_HISTORICAL_BACKGROUND_LENGTH


# --- Property 7: Historical highlights organization ---


@pytest.mark.asyncio
@given(inputs=_spot_info_inputs())
@settings(max_examples=100)
async def test_property_historical_highlights_organization(
    inputs: tuple[str, dict[str, Any]],
) -> None:
    """Property 7: Historical highlights organizationを検証する

    前提条件:
    - 任意の観光スポット情報入力が生成される
    - 構造化データ生成のためのresponse_schemaが定義されている

    検証項目:
    - GeminiAIService.generate_structured_data()が構造化データを生成すること
    - GeminiClient.generate_content_with_schema()が正しいスキーマとtemperature=0.0で呼び出されること
    - SpotDetailが正しく生成されること
    - highlightsフィールドが非空のタプルであること
    - 各highlightが非空文字列であること
    - highlightsが少なくとも1つの要素を含むこと（response_schemaのminItems: 1に対応）
    """
    prompt, response_schema = inputs

    # モックGeminiClientの準備
    mock_client = MagicMock(spec=GeminiClient)
    mock_spot_data = {
        "spot_name": "Historical Castle",
        "historical_background": "This castle was built in 1397 AD.",
        "highlights": [
            "Main Keep built in 1397",
            "Stone walls from Edo period",
            "Historical artifacts museum",
        ],
        "recommended_visit_time": "Afternoon",
        "historical_significance": "Symbol of feudal era",
    }
    mock_client.generate_content_with_schema = AsyncMock(return_value=mock_spot_data)

    # GeminiAIServiceのインスタンス作成
    service = GeminiAIService(
        gemini_client=mock_client,
        default_temperature=0.0,
        default_max_output_tokens=8192,
        default_timeout_seconds=60,
    )

    # 実行: 構造化データ生成
    result = await service.generate_structured_data(
        prompt=prompt,
        response_schema=response_schema,
    )

    # 検証1: GeminiClient.generate_content_with_schema()が適切に呼び出されること
    mock_client.generate_content_with_schema.assert_called_once()
    call_kwargs = mock_client.generate_content_with_schema.call_args.kwargs
    assert call_kwargs["prompt"] == prompt
    assert call_kwargs["response_schema"] == response_schema

    # 検証2: デフォルトtemperature=0.0が使用されること（構造化出力推奨値）
    assert call_kwargs["temperature"] == 0.0

    # 検証3: 構造化データが返されること
    assert isinstance(result, dict)
    assert "highlights" in result

    # 検証4: SpotDetailが正しく生成できること
    spot_detail = SpotDetail(
        spot_name=result["spot_name"],
        historical_background=result["historical_background"],
        highlights=tuple(result["highlights"]),
        recommended_visit_time=result["recommended_visit_time"],
        historical_significance=result["historical_significance"],
    )

    # 検証5: highlightsが非空のタプルであること
    assert spot_detail.highlights
    assert isinstance(spot_detail.highlights, tuple)

    # 検証6: 各highlightが非空文字列であること
    for highlight in spot_detail.highlights:
        assert highlight
        assert highlight.strip() != ""

    # 検証7: highlightsが少なくとも1つの要素を含むこと（response_schemaのminItems: 1に対応）
    assert len(spot_detail.highlights) >= 1
