# エージェント設計の基本原則

## はじめに

AI Agent設計における3つの基本原則について詳細に解説する。これらの原則は、保守可能で効果的なエージェントシステムを構築するための基盤となる。

## 1. シンプリシティ優先

### 原則

**常にシンプルなソリューションから始める。複雑性は、実測で改善が確認できる場合のみ追加する。**

不要な複雑性は、デバッグを困難にし、レイテンシとコストを増大させる。多くの場合、適切に設計された単一プロンプトや簡素なプロンプト連鎖で十分な結果が得られる。

### なぜ重要か

**デバッグの容易性**
シンプルなシステムは、問題の特定と修正が容易である。複雑なマルチエージェントシステムでは、エラーの原因を特定することが困難になる。

**コストとレイテンシ**
各LLM呼び出しはコストとレイテンシを増加させる。不要なステップを追加することは、投資対効果を低下させる。

**保守性**
シンプルなシステムは、将来の変更や拡張が容易である。過度に複雑なシステムは、変更のリスクが高く、保守コストが増大する。

**反復改善**
シンプルなベースラインから始めることで、どの複雑性が実際に価値をもたらすかを測定できる。

### 実践ガイド

#### ステップ1: 単一プロンプトで試す

まず、タスクを単一のプロンプトで解決できないか検証する。

```python
# 最初のアプローチ: シンプルな単一プロンプト
def analyze_text(text):
    prompt = f"""
以下のテキストを分析し、主要なテーマを抽出してください。

テキスト: {text}

主要なテーマを箇条書きで提供してください。
"""
    result = call_llm(prompt)
    return result
```

単一プロンプトが不十分な場合のみ、次のステップに進む。

#### ステップ2: 最小限のプロンプト連鎖

タスクを2-3ステップに分解し、各ステップの必要性を検証する。

```python
# 2ステップのプロンプト連鎖
def analyze_text_chained(text):
    # ステップ1: キーワード抽出
    keywords = extract_keywords(text)

    # ステップ2: テーマ分類
    themes = classify_themes(keywords)

    return themes
```

各ステップが実際に品質を向上させるか測定する。

#### ステップ3: 実測で複雑性を追加

複雑性を追加する前に、以下を実測する：

- **精度の向上**: 新しいステップが精度を向上させるか
- **レイテンシの影響**: 追加時間が許容範囲か
- **コストの増加**: 追加コストが投資対効果に見合うか

測定可能な改善がない場合は、複雑性を追加しない。

#### ステップ4: 段階的な拡張

一度にすべてを実装せず、段階的に機能を追加する。

```python
# 段階1: 基本機能
def process_v1(data):
    return basic_processing(data)

# 段階2: 評価を追加（実測で効果を確認）
def process_v2(data):
    result = basic_processing(data)
    if needs_improvement(result):
        result = improve(result)
    return result

# 段階3: 並列化を追加（レイテンシが問題の場合のみ）
def process_v3(data):
    # 並列化の実装
    pass
```

### Before/After例

#### Before（過度な複雑性）

```python
def answer_question(question):
    # 複雑なマルチエージェントシステム
    # オーケストレーターが計画を立てる
    plan = orchestrator.create_plan(question)

    # 複数のワーカーを並列実行
    workers = [
        researcher_agent,
        analyzer_agent,
        validator_agent,
        optimizer_agent
    ]
    results = run_parallel(workers, plan)

    # 評価者が結果を評価
    evaluation = evaluator.assess(results)

    # 評価が不十分なら再実行
    if evaluation.score < 0.8:
        results = rerun_with_improvements(results, evaluation)

    # 最終統合
    answer = integrator.combine(results)

    return answer

# 問題点:
# - 単純な質問にも複雑なワークフローを実行
# - 多数のLLM呼び出しでコストが高い（$0.50/質問）
# - レイテンシが長い（30秒）
# - デバッグが困難
# - 実際の精度向上は限定的（単一プロンプトと比較して+5%のみ）
```

#### After（シンプリシティ優先）

```python
def answer_question(question):
    # まずシンプルなアプローチを試す
    prompt = f"""
以下の質問に回答してください。

質問: {question}

明確で簡潔な回答を提供してください。
"""
    answer = call_llm(prompt)
    return answer

# 測定結果:
# - コスト: $0.02/質問（96%削減）
# - レイテンシ: 3秒（90%削減）
# - デバッグが容易
# - 精度: 単純な質問では85%（複雑なシステムと同等）

# 複雑な質問のみ、追加ステップを適用
def answer_complex_question(question):
    # ステップ1: 情報収集
    context = search_information(question)

    # ステップ2: 回答生成
    answer = generate_answer(question, context)

    return answer

# 測定結果（複雑な質問のみ）:
# - コスト: $0.10/質問（80%削減）
# - レイテンシ: 8秒（73%削減）
# - 精度: 90%（+5%向上）
```

#### 改善ポイント

- **シンプルなケースには軽量なアプローチ**: 大多数の質問（80%）は単一プロンプトで十分
- **複雑なケースのみ追加ステップ**: 必要な場合のみプロンプト連鎖を使用
- **段階的な複雑性**: 一度にすべてを実装せず、必要に応じて追加
- **測定可能な改善**: 各ステップの効果を実測

## 2. 透明性とデバッグ容易性

### 原則

**各ステップの入出力を明示的に記録し、システムの動作を追跡可能にする。**

問題の特定と修正には、システムの内部状態を観察できることが不可欠である。透明性の高い設計は、改善サイクルを加速する。

### なぜ重要か

**問題の早期発見**
各ステップの出力を記録することで、どこで問題が発生したかを即座に特定できる。

**反復改善**
中間結果を可視化することで、どのステップが改善を必要としているかを判断できる。

**ユーザー信頼**
エージェントの思考プロセスを明示することで、ユーザーの信頼を獲得できる。

**コラボレーション**
透明なシステムは、チームメンバー間での理解と改善が容易である。

### 実践ガイド

#### ログとモニタリング

各エージェント呼び出しの入出力をログに記録する。

```python
import logging

def process_with_logging(input_data):
    logger = logging.getLogger(__name__)

    # ステップ1のログ
    logger.info(f"Step 1: Input = {input_data}")
    result_1 = step_1(input_data)
    logger.info(f"Step 1: Output = {result_1}")

    # ステップ2のログ
    logger.info(f"Step 2: Input = {result_1}")
    result_2 = step_2(result_1)
    logger.info(f"Step 2: Output = {result_2}")

    return result_2
```

#### 構造化されたログ

JSON形式でログを記録し、分析を容易にする。

```python
import json
import time

def process_with_structured_logging(input_data):
    trace_id = generate_trace_id()

    # ステップ1
    start_time = time.time()
    result_1 = step_1(input_data)
    end_time = time.time()

    log_entry = {
        "trace_id": trace_id,
        "step": "step_1",
        "input": input_data,
        "output": result_1,
        "duration_ms": (end_time - start_time) * 1000,
        "timestamp": time.time()
    }
    logger.info(json.dumps(log_entry))

    # ステップ2以降も同様
    return result_2
```

#### Thinking Tagsの使用

LLMに計画プロセスを明示させる。

```python
def process_with_thinking(task):
    prompt = f"""
以下のタスクを実行してください。

<thinking>タグ内で、タスクを分析し、実行計画を立ててください。

タスク: {task}

<thinking>
[ここでタスクを分析し、計画を立てる]
</thinking>

[計画に基づいて実行]
"""
    result = call_llm(prompt)
    return result
```

#### 中間結果の可視化

ユーザーに中間ステップを提示する。

```python
def process_with_visibility(input_data):
    print("ステップ1: データ収集中...")
    data = collect_data(input_data)
    print(f"収集完了: {len(data)}件の情報")

    print("\nステップ2: データ分析中...")
    analysis = analyze_data(data)
    print(f"分析完了: {len(analysis['insights'])}件のインサイト")

    print("\nステップ3: レポート生成中...")
    report = generate_report(analysis)
    print("レポート生成完了")

    return report
```

### Before/After例

#### Before（不透明なシステム）

```python
def process_customer_feedback(feedback):
    # ブラックボックス処理
    result = complex_processing(feedback)
    return result

# 問題点:
# - 中間ステップが不明
# - エラーが発生した際にどこで問題が起きたか不明
# - 改善のためにどのステップを最適化すべきか判断できない
# - デバッグに多大な時間がかかる
```

#### After（透明性の高いシステム）

```python
def process_customer_feedback_transparent(feedback):
    logger = logging.getLogger(__name__)
    trace_id = generate_trace_id()

    # ステップ1: 感情分析
    logger.info(f"[{trace_id}] Step 1: Sentiment Analysis")
    logger.debug(f"[{trace_id}] Input: {feedback[:100]}...")

    sentiment = analyze_sentiment(feedback)

    logger.info(f"[{trace_id}] Step 1 Output: {sentiment}")

    # ステップ2: テーマ抽出
    logger.info(f"[{trace_id}] Step 2: Theme Extraction")

    themes = extract_themes(feedback)

    logger.info(f"[{trace_id}] Step 2 Output: {len(themes)} themes found")
    logger.debug(f"[{trace_id}] Themes: {themes}")

    # ステップ3: 改善提案
    logger.info(f"[{trace_id}] Step 3: Generating Recommendations")

    recommendations = generate_recommendations(sentiment, themes)

    logger.info(f"[{trace_id}] Step 3 Output: {len(recommendations)} recommendations")

    # 最終結果
    result = {
        "trace_id": trace_id,
        "sentiment": sentiment,
        "themes": themes,
        "recommendations": recommendations
    }

    logger.info(f"[{trace_id}] Processing Complete")

    return result

# 改善ポイント:
# - 各ステップの入出力が明確
# - trace_idで全体のフローを追跡可能
# - エラー発生時に即座に問題箇所を特定
# - 各ステップのパフォーマンスを測定可能
# - 改善すべきステップを特定しやすい
```

#### 改善ポイント

- **トレーサビリティ**: trace_idで全体のフローを追跡
- **ステップの可視化**: 各ステップの開始と完了を記録
- **詳細なログ**: 入出力を記録し、後から分析可能
- **デバッグの容易性**: エラー発生時に即座に問題箇所を特定

## 3. モジュール性と再利用性

### 原則

**各コンポーネントを独立した機能単位として設計し、再利用可能にする。**

モジュール化により、システムの一部を独立して改善・テストできる。新しいユースケースへの拡張も容易になる。

### なぜ重要か

**独立したテスト**
各モジュールを独立してテストできるため、品質保証が容易である。

**部分的な改善**
システム全体を変更することなく、特定のモジュールを改善できる。

**再利用性**
同じモジュールを複数のワークフローで再利用できる。

**チーム開発**
モジュール化により、複数の開発者が並行して作業できる。

### 実践ガイド

#### 単一責任の原則

各モジュールは1つの明確な役割を持つようにする。

```python
# 良い例: 単一責任
def extract_keywords(text):
    """テキストからキーワードを抽出する"""
    # キーワード抽出のみに集中
    pass

def classify_themes(keywords):
    """キーワードをテーマに分類する"""
    # テーマ分類のみに集中
    pass

# 悪い例: 複数の責任
def extract_and_classify(text):
    """キーワード抽出とテーマ分類を両方実行"""
    # 2つの異なる責任を持つ
    pass
```

#### 明確なインターフェース

各モジュールの入出力を明確に定義する。

```python
from typing import List, Dict

def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    テキストの感情を分析する。

    Args:
        text: 分析対象のテキスト

    Returns:
        感情スコアの辞書（positive, negative, neutral）
    """
    prompt = f"以下のテキストの感情を分析してください: {text}"
    result = call_llm(prompt)

    return {
        "positive": result.positive_score,
        "negative": result.negative_score,
        "neutral": result.neutral_score
    }
```

#### 疎結合

モジュール間の依存を最小化する。

```python
# 良い例: 疎結合
def process_data(data, analyzer, reporter):
    """
    データ処理のワークフロー。
    analyzerとreporterを外部から注入。
    """
    analysis = analyzer.analyze(data)
    report = reporter.generate(analysis)
    return report

# 悪い例: 密結合
def process_data(data):
    """
    特定のAnalyzerとReporterに依存。
    """
    analyzer = SpecificAnalyzer()  # 密結合
    reporter = SpecificReporter()  # 密結合
    analysis = analyzer.analyze(data)
    report = reporter.generate(analysis)
    return report
```

#### 共通機能の抽出

複数のワークフローで使用される機能を共通モジュールとして抽出する。

```python
# 共通モジュール: text_processing.py
def preprocess_text(text: str) -> str:
    """テキストの前処理（複数のワークフローで使用）"""
    text = text.strip()
    text = text.lower()
    return text

def chunk_text(text: str, max_length: int) -> List[str]:
    """テキストをチャンクに分割（複数のワークフローで使用）"""
    # チャンク化の実装
    pass

# ワークフロー1: sentiment_analysis.py
from text_processing import preprocess_text, chunk_text

def analyze_sentiment(text: str):
    text = preprocess_text(text)  # 共通機能を再利用
    chunks = chunk_text(text, 1000)  # 共通機能を再利用
    # 感情分析の実装
    pass

# ワークフロー2: theme_extraction.py
from text_processing import preprocess_text, chunk_text

def extract_themes(text: str):
    text = preprocess_text(text)  # 共通機能を再利用
    chunks = chunk_text(text, 1000)  # 共通機能を再利用
    # テーマ抽出の実装
    pass
```

### Before/After例

#### Before（モノリシックなシステム）

```python
def customer_support_agent(ticket):
    # すべてが1つの巨大な関数
    # チケットタイプの判定
    if "billing" in ticket.lower():
        category = "billing"
    elif "bug" in ticket.lower():
        category = "technical"
    else:
        category = "general"

    # カテゴリに応じた処理（すべてが1つの関数内）
    if category == "billing":
        # 請求情報取得
        billing_info = get_billing_info(ticket)
        # 請求分析
        analysis = analyze_billing(billing_info)
        # 回答生成
        response = generate_billing_response(analysis)
    elif category == "technical":
        # 技術診断
        diagnosis = diagnose_technical(ticket)
        # 解決策生成
        solution = generate_solution(diagnosis)
        # 回答生成
        response = generate_technical_response(solution)
    else:
        # FAQ検索
        faq = search_faq(ticket)
        # 回答生成
        response = generate_general_response(faq)

    return response

# 問題点:
# - すべてのロジックが1つの関数に詰め込まれている
# - 再利用できない
# - テストが困難
# - 変更のリスクが高い
# - 新しいカテゴリの追加が困難
```

#### After（モジュール化されたシステム）

```python
# modules/categorizer.py
class TicketCategorizer:
    """チケットのカテゴリ分類"""
    def categorize(self, ticket: str) -> str:
        prompt = f"以下のチケットを分類してください: {ticket}"
        result = call_llm(prompt)
        return result.category

# modules/billing_handler.py
class BillingHandler:
    """請求関連の処理"""
    def handle(self, ticket: str) -> str:
        billing_info = self._get_billing_info(ticket)
        analysis = self._analyze_billing(billing_info)
        response = self._generate_response(analysis)
        return response

    def _get_billing_info(self, ticket: str):
        # 請求情報取得
        pass

    def _analyze_billing(self, billing_info):
        # 請求分析
        pass

    def _generate_response(self, analysis):
        # 回答生成
        pass

# modules/technical_handler.py
class TechnicalHandler:
    """技術的問題の処理"""
    def handle(self, ticket: str) -> str:
        diagnosis = self._diagnose(ticket)
        solution = self._generate_solution(diagnosis)
        response = self._generate_response(solution)
        return response

    def _diagnose(self, ticket: str):
        # 技術診断
        pass

    def _generate_solution(self, diagnosis):
        # 解決策生成
        pass

    def _generate_response(self, solution):
        # 回答生成
        pass

# modules/general_handler.py
class GeneralHandler:
    """一般的な問い合わせの処理"""
    def handle(self, ticket: str) -> str:
        faq = self._search_faq(ticket)
        response = self._generate_response(faq)
        return response

    def _search_faq(self, ticket: str):
        # FAQ検索
        pass

    def _generate_response(self, faq):
        # 回答生成
        pass

# main workflow
def customer_support_agent(ticket: str) -> str:
    # モジュールを組み合わせてワークフローを構築
    categorizer = TicketCategorizer()
    handlers = {
        "billing": BillingHandler(),
        "technical": TechnicalHandler(),
        "general": GeneralHandler()
    }

    # カテゴリ分類
    category = categorizer.categorize(ticket)

    # 適切なハンドラーを選択
    handler = handlers.get(category, handlers["general"])

    # 処理を実行
    response = handler.handle(ticket)

    return response

# 改善ポイント:
# - 各モジュールが独立している
# - 各モジュールを個別にテスト可能
# - 新しいハンドラーの追加が容易（新しいクラスを追加するだけ）
# - 各モジュールを独立して改善可能
# - 他のワークフローでハンドラーを再利用可能
```

#### 改善ポイント

- **単一責任**: 各クラスが1つの明確な役割を持つ
- **独立したテスト**: 各モジュールを個別にテスト可能
- **拡張性**: 新しいハンドラーの追加が容易
- **再利用性**: 他のワークフローでモジュールを再利用可能
- **保守性**: システムの一部を変更しても他の部分に影響しない

## まとめ

### 3つの基本原則の相互関係

**シンプリシティ → 透明性 → モジュール性**

1. シンプルなシステムから始める
2. 透明性を確保してデバッグと改善を容易にする
3. モジュール化して再利用性と保守性を向上させる

### 実践のチェックリスト

**シンプリシティ**
- [ ] 単一プロンプトで試したか？
- [ ] 各ステップの必要性を実測で検証したか？
- [ ] 複雑性を追加する前に効果を測定したか？

**透明性**
- [ ] 各ステップの入出力をログに記録しているか？
- [ ] trace_idで全体のフローを追跡できるか？
- [ ] エラー発生時に問題箇所を即座に特定できるか？

**モジュール性**
- [ ] 各モジュールが単一責任を持つか？
- [ ] インターフェースが明確に定義されているか？
- [ ] モジュール間の結合度が低いか？
- [ ] 共通機能を抽出して再利用しているか？

### 次のステップ

- ワークフローパターンの詳細: [workflow-patterns-detail.md](workflow-patterns-detail.md)
- ツール統合のベストプラクティス: [tool-integration.md](tool-integration.md)
- アンチパターンと回避方法: [anti-patterns.md](anti-patterns.md)
