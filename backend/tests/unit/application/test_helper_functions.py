"""ヘルパー関数の動作確認テスト"""

from app.application.use_cases.generate_travel_guide import (
    _build_allowed_related_spots_text,
    _assess_fact_extraction_coverage,
    _build_fact_extraction_retry_prompt,
    _build_spot_source_constraints_text,
    _build_travel_guide_prompt,
    _create_tourist_spots,
    _detect_new_spots,
    _normalize_spot_name,
)
from app.domain.travel_guide.value_objects import SpotDetail
from app.domain.travel_plan.entity import TouristSpot
from app.domain.travel_plan.entity import TravelPlan


def test_normalize_spot_name_trims_whitespace() -> None:
    """空白文字のトリミングを確認"""
    assert _normalize_spot_name("  清水寺  ") == "清水寺"
    assert _normalize_spot_name("金閣寺") == "金閣寺"
    assert _normalize_spot_name("\t二条城\n") == "二条城"


def test_normalize_spot_name_preserves_case() -> None:
    """大文字小文字の保持を確認"""
    assert _normalize_spot_name("Tokyo Tower") == "Tokyo Tower"
    assert _normalize_spot_name("KYOTO") == "KYOTO"


def test_detect_new_spots_with_new_spots() -> None:
    """新規スポットのみの場合"""
    spot_details = [
        SpotDetail(
            spot_name="二条城",
            historical_background="test",
            highlights=("test",),
            recommended_visit_time="test",
            historical_significance="test",
        ),
    ]
    existing_spots = [
        TouristSpot(id="1", name="清水寺", description=None, user_notes=None),
    ]
    result = _detect_new_spots(spot_details, existing_spots)
    assert result == ["二条城"]


def test_detect_new_spots_with_existing_only() -> None:
    """既存スポットのみの場合"""
    spot_details = [
        SpotDetail(
            spot_name="清水寺",
            historical_background="test",
            highlights=("test",),
            recommended_visit_time="test",
            historical_significance="test",
        ),
    ]
    existing_spots = [
        TouristSpot(id="1", name="清水寺", description=None, user_notes=None),
    ]
    result = _detect_new_spots(spot_details, existing_spots)
    assert result == []


def test_detect_new_spots_with_duplicates_in_spot_details() -> None:
    """spotDetails内の重複排除を確認"""
    spot_details = [
        SpotDetail(
            spot_name="二条城",
            historical_background="test",
            highlights=("test",),
            recommended_visit_time="test",
            historical_significance="test",
        ),
        SpotDetail(
            spot_name="二条城",
            historical_background="test2",
            highlights=("test2",),
            recommended_visit_time="test2",
            historical_significance="test2",
        ),
    ]
    existing_spots = [
        TouristSpot(id="1", name="清水寺", description=None, user_notes=None),
    ]
    result = _detect_new_spots(spot_details, existing_spots)
    assert result == ["二条城"]  # 最初の出現のみ


def test_create_tourist_spots_creates_spots() -> None:
    """TouristSpotの作成を確認"""
    new_spot_names = ["二条城", "伏見稲荷大社"]
    result = _create_tourist_spots(new_spot_names)
    assert len(result) == 2
    assert result[0].name == "二条城"
    assert result[1].name == "伏見稲荷大社"
    assert result[0].description is None
    assert result[0].user_notes is None
    assert result[1].description is None
    assert result[1].user_notes is None


def test_create_tourist_spots_generates_unique_ids() -> None:
    """IDの一意性を確認"""
    new_spot_names = ["スポット1", "スポット2", "スポット3"]
    result = _create_tourist_spots(new_spot_names)
    ids = [spot.id for spot in result]
    assert len(ids) == len(set(ids))  # すべてのIDが一意



def test_assess_fact_extraction_coverage_detects_missing_sources() -> None:
    """スポットごとの出典不足を検出できることを確認。"""
    extracted_facts = """
- 清水寺: 歴史的背景 [清水寺公式](https://www.kiyomizudera.or.jp/) [検証: valid]
- 金閣寺: 歴史的背景のみ（URLなし）
"""
    summary = _assess_fact_extraction_coverage(
        extracted_facts=extracted_facts,
        spot_names=["清水寺", "金閣寺"],
    )

    assert summary["sufficient"] is False
    assert "金閣寺" in summary["missing_spot_sources"]


def test_build_fact_extraction_retry_prompt_includes_missing_spots() -> None:
    """再抽出プロンプトに不足スポットが含まれることを確認。"""
    retry_prompt = _build_fact_extraction_retry_prompt(
        base_prompt="元プロンプト",
        previous_extracted_facts="前回結果",
        missing_spot_sources=["清水寺", "金閣寺"],
        min_required_urls=4,
        feedback_round=1,
    )

    assert "清水寺" in retry_prompt
    assert "金閣寺" in retry_prompt
    assert "4 件以上" in retry_prompt
    assert "同義語・旧称・英語表記" in retry_prompt
    assert "vertexaisearch.cloud.google.com/grounding-api-redirect" in retry_prompt


def test_build_fact_extraction_retry_prompt_reuses_validated_urls_when_sufficient() -> None:
    """必要件数を満たした場合は新規URL追加を抑制する指示が含まれること。"""
    previous = """
- 清水寺 [出典: https://example.com/kiyomizu] [検証: valid]
- 金閣寺 [出典: https://example.com/kinkaku] [検証: valid]
"""
    retry_prompt = _build_fact_extraction_retry_prompt(
        base_prompt="元プロンプト",
        previous_extracted_facts=previous,
        missing_spot_sources=["清水寺"],
        min_required_urls=2,
        feedback_round=2,
    )

    assert "必要件数（2件）を満たしています" in retry_prompt
    assert "新しいURLは原則として追加しない" in retry_prompt
    assert "https://example.com/kiyomizu" in retry_prompt


def test_build_fact_extraction_retry_prompt_adds_only_required_number_of_new_urls() -> None:
    """必要件数に足りない場合は不足分のみ追加する指示が含まれること。"""
    previous = """
- 清水寺 [出典: https://example.com/kiyomizu] [検証: valid]
"""
    retry_prompt = _build_fact_extraction_retry_prompt(
        base_prompt="元プロンプト",
        previous_extracted_facts=previous,
        missing_spot_sources=["金閣寺"],
        min_required_urls=3,
        feedback_round=3,
    )

    assert "有効な出典URLは 1 件" in retry_prompt
    assert "不足している 2 件分のみ" in retry_prompt
    assert "3回目以降の再試行" in retry_prompt


def test_build_spot_source_constraints_text_assigns_validated_urls_per_spot() -> None:
    """スポット別制約に検証済みURLが正しく割り当てられること。"""
    plan = TravelPlan(
        id="plan-1",
        user_id="user-1",
        title="沖縄の戦跡巡り",
        destination="沖縄",
        spots=[
            TouristSpot(id="spot-1", name="ひめゆりの塔", description=None, user_notes=None),
            TouristSpot(id="spot-2", name="首里城", description=None, user_notes=None),
        ],
    )
    extracted_facts = """
## スポット別の事実
### ひめゆりの塔
- 学徒隊の慰霊碑である [出典: https://example.com/himeyuri] [検証: valid]
### 首里城
- 琉球王国の象徴である [出典: https://example.com/shuri] [検証: valid]
"""

    constraints = _build_spot_source_constraints_text(plan, extracted_facts)

    assert "- ひめゆりの塔:" in constraints
    assert "- 首里城:" in constraints
    assert "https://example.com/himeyuri" in constraints
    assert "https://example.com/shuri" in constraints


def test_build_spot_source_constraints_text_marks_missing_sources() -> None:
    """検証済みURLがないスポットは出典不足として明示されること。"""
    plan = TravelPlan(
        id="plan-2",
        user_id="user-2",
        title="奈良の寺社巡り",
        destination="奈良",
        spots=[
            TouristSpot(id="spot-1", name="東大寺", description=None, user_notes=None),
            TouristSpot(id="spot-2", name="春日大社", description=None, user_notes=None),
        ],
    )
    extracted_facts = """
## スポット別の事実
### 東大寺
- 奈良時代の大仏建立 [出典: https://example.com/todaiji] [検証: valid]
### 春日大社
- 祭礼の歴史がある（URLなし）
"""

    constraints = _build_spot_source_constraints_text(plan, extracted_facts)

    assert "- 東大寺:" in constraints
    assert "- 春日大社:" in constraints
    assert "https://example.com/todaiji" in constraints
    assert "春日大社" in constraints
    assert "URLなし（出典不足）" in constraints


def test_build_allowed_related_spots_text_includes_destination_and_user_spots() -> None:
    """relatedSpots許可一覧に目的地とユーザー指定スポットが含まれること。"""
    plan = TravelPlan(
        id="plan-3",
        user_id="user-3",
        title="伊勢志摩",
        destination="鳥羽市",
        spots=[
            TouristSpot(id="spot-1", name="伊勢神宮", description=None, user_notes=None),
            TouristSpot(id="spot-2", name="夫婦岩", description=None, user_notes=None),
        ],
    )

    allowed_text = _build_allowed_related_spots_text(plan)

    assert "- 鳥羽市" in allowed_text
    assert "- 伊勢神宮" in allowed_text
    assert "- 夫婦岩" in allowed_text


def test_build_travel_guide_prompt_includes_related_spot_constraints() -> None:
    """旅行ガイド生成プロンプトにrelatedSpots制約が埋め込まれること。"""
    plan = TravelPlan(
        id="plan-4",
        user_id="user-4",
        title="伊勢志摩",
        destination="鳥羽市",
        spots=[
            TouristSpot(id="spot-1", name="伊勢神宮", description=None, user_notes=None),
        ],
    )
    extracted_facts = """
## スポット別の事実
### 伊勢神宮
- 由緒ある神社 [出典: https://example.com/ise] [検証: valid]
"""

    prompt = _build_travel_guide_prompt(
        plan,
        extracted_facts,
        related_spots_retry_feedback="timeline.relatedSpots を修正してください。",
    )

    assert "<allowed_related_spots>" in prompt
    assert "伊勢神宮" in prompt
    assert "鳥羽市" in prompt
    assert "timeline.relatedSpots を修正してください。" in prompt
