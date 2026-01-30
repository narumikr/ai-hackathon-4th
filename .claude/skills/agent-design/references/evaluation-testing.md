# 評価とテスト戦略

## はじめに

AI Agentシステムの品質を保証するには、適切な評価とテストが不可欠である。このドキュメントでは、評価方法、重要メトリクス、テスト戦略について解説する。

## 評価方法

### 1. コードベース評価（Code-Based Evaluation）

**概要**
決定論的なルールやコードで出力を評価する方法。最も高速でコスト効率が良い。

**使用場面**
- 明確な正解がある場合
- フォーマットや構造の検証
- 数値計算の正確性確認
- JSONスキーマの検証

**実装例**

```python
def evaluate_json_output(output: str, expected_schema: dict) -> dict:
    """JSONスキーマで出力を検証"""
    try:
        # JSONとしてパース
        data = json.loads(output)

        # スキーマ検証
        validate(data, expected_schema)

        return {
            "valid": True,
            "score": 100,
            "errors": []
        }
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "score": 0,
            "errors": [f"JSON解析エラー: {e}"]
        }
    except ValidationError as e:
        return {
            "valid": False,
            "score": 50,
            "errors": [f"スキーマ検証エラー: {e}"]
        }

def evaluate_code_execution(code: str, test_cases: list) -> dict:
    """テストケースでコードを評価"""
    passed = 0
    failed = 0
    errors = []

    for test in test_cases:
        try:
            result = execute_code(code, test["input"])
            if result == test["expected"]:
                passed += 1
            else:
                failed += 1
                errors.append(f"入力 {test['input']}: 期待値 {test['expected']}, 実際 {result}")
        except Exception as e:
            failed += 1
            errors.append(f"実行エラー: {e}")

    total = passed + failed
    score = (passed / total * 100) if total > 0 else 0

    return {
        "valid": failed == 0,
        "score": score,
        "passed": passed,
        "failed": failed,
        "errors": errors
    }
```

**利点**
- 高速で即座に結果が得られる
- コストがかからない
- 一貫性のある評価

**制約**
- 主観的な品質は評価できない
- 創造的なタスクには不向き
- すべてのケースをカバーするルールの作成が困難

### 2. モデルベース評価（Model-Based Evaluation）

**概要**
別のLLMに出力を評価させる方法。主観的な品質も評価できる。

**使用場面**
- 創造的なタスクの評価
- トーンやスタイルの検証
- 意味的な正確性の確認
- 複雑な品質基準の適用

**実装例**

```python
def evaluate_with_llm(output: str, criteria: dict, reference: str = None) -> dict:
    """LLMで出力を評価"""
    criteria_text = "\n".join([
        f"- {name}: {desc['description']} (重み: {desc['weight']})"
        for name, desc in criteria.items()
    ])

    reference_section = ""
    if reference:
        reference_section = f"\n参照回答（理想的な回答例）:\n{reference}\n"

    prompt = f"""
以下の出力を評価してください。

出力:
{output}
{reference_section}
評価基準:
{criteria_text}

各基準について0-100点で評価し、以下のJSON形式で出力してください:
{{
  "scores": {{
    "基準名": {{
      "score": 点数,
      "reasoning": "評価理由"
    }},
    ...
  }},
  "overall_score": 全体スコア（加重平均）,
  "strengths": ["強み1", "強み2", ...],
  "weaknesses": ["弱点1", "弱点2", ...]
}}
"""
    result = call_llm(prompt, temperature=0.2)
    evaluation = json.loads(result)

    return evaluation

# 実行例
criteria = {
    "accuracy": {
        "description": "情報の正確性",
        "weight": 0.4
    },
    "clarity": {
        "description": "明確性と読みやすさ",
        "weight": 0.3
    },
    "completeness": {
        "description": "情報の完全性",
        "weight": 0.3
    }
}

evaluation = evaluate_with_llm(
    output="生成された回答",
    criteria=criteria,
    reference="理想的な回答例（オプション）"
)
```

**利点**
- 主観的な品質も評価可能
- 人間の判断に近い評価
- 柔軟な評価基準の適用

**制約**
- コストがかかる
- レイテンシが発生
- 評価の一貫性に課題がある場合も

### 3. ヒューマングレーダー（Human Grading）

**概要**
人間が出力を評価する方法。最も信頼性が高いが、コストとスケーラビリティに課題がある。

**使用場面**
- 最終的な品質確認
- モデルベース評価の検証
- 複雑で主観的なタスク
- 新しいユースケースの初期評価

**実装例**

```python
def create_human_evaluation_task(output: str, criteria: dict) -> dict:
    """人間評価用のタスクを作成"""
    task = {
        "task_id": generate_task_id(),
        "output": output,
        "criteria": criteria,
        "questions": [
            {
                "id": "overall_quality",
                "question": "全体的な品質を1-5で評価してください",
                "type": "rating",
                "scale": [1, 2, 3, 4, 5]
            }
        ]
    }

    # 各評価基準について質問を追加
    for criterion_name, criterion_info in criteria.items():
        task["questions"].append({
            "id": criterion_name,
            "question": f"{criterion_info['description']}を1-5で評価してください",
            "type": "rating",
            "scale": [1, 2, 3, 4, 5]
        })

    # 自由記述の質問を追加
    task["questions"].extend([
        {
            "id": "strengths",
            "question": "この出力の強みは何ですか？",
            "type": "text"
        },
        {
            "id": "improvements",
            "question": "どのように改善できますか？",
            "type": "text"
        }
    ])

    return task

def analyze_human_evaluations(evaluations: list) -> dict:
    """複数の人間評価を分析"""
    # 各基準の平均スコアを計算
    criterion_scores = {}
    for eval in evaluations:
        for answer in eval["answers"]:
            if answer["type"] == "rating":
                criterion = answer["id"]
                score = answer["value"]

                if criterion not in criterion_scores:
                    criterion_scores[criterion] = []
                criterion_scores[criterion].append(score)

    # 統計値を計算
    results = {}
    for criterion, scores in criterion_scores.items():
        results[criterion] = {
            "mean": sum(scores) / len(scores),
            "median": sorted(scores)[len(scores) // 2],
            "std": calculate_std(scores),
            "count": len(scores)
        }

    # 自由記述をまとめる
    strengths = []
    improvements = []
    for eval in evaluations:
        for answer in eval["answers"]:
            if answer["id"] == "strengths":
                strengths.append(answer["value"])
            elif answer["id"] == "improvements":
                improvements.append(answer["value"])

    return {
        "criterion_scores": results,
        "strengths": strengths,
        "improvements": improvements
    }
```

**利点**
- 最も信頼性が高い
- 微妙なニュアンスも評価可能
- 新しい評価基準の発見

**制約**
- コストが高い
- スケールしない
- 時間がかかる
- 評価者間のばらつき

## 重要メトリクス

### 1. 精度（Accuracy）

**定義**
出力が期待される結果と一致する割合。

**測定方法**

```python
def calculate_accuracy(predictions: list, ground_truth: list) -> float:
    """精度を計算"""
    if len(predictions) != len(ground_truth):
        raise ValueError("予測と正解のサイズが一致しません")

    correct = sum(p == g for p, g in zip(predictions, ground_truth))
    total = len(predictions)

    return correct / total if total > 0 else 0

# 実行例
predictions = ["A", "B", "C", "A", "B"]
ground_truth = ["A", "B", "C", "B", "B"]
accuracy = calculate_accuracy(predictions, ground_truth)
# 結果: 0.8 (80%)
```

**使用場面**
- 分類タスク
- 質問応答タスク
- コード生成の正確性

### 2. レイテンシ（Latency）

**定義**
タスク完了までの時間。

**測定方法**

```python
import time

def measure_latency(func, *args, **kwargs) -> dict:
    """関数のレイテンシを測定"""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()

    latency_ms = (end_time - start_time) * 1000

    return {
        "result": result,
        "latency_ms": latency_ms
    }

# 実行例
def process_task(input_data):
    # タスク処理
    return "結果"

measurement = measure_latency(process_task, "入力データ")
print(f"レイテンシ: {measurement['latency_ms']:.2f}ms")
```

**使用場面**
- ユーザー体験の最適化
- リアルタイムアプリケーション
- コスト最適化（時間=コスト）

### 3. コスト（Cost）

**定義**
タスク実行にかかるLLM APIの費用。

**測定方法**

```python
def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """APIコストを計算"""
    # モデルごとの料金（例）
    pricing = {
        "haiku": {
            "input": 0.25 / 1_000_000,   # $0.25 per MTok
            "output": 1.25 / 1_000_000   # $1.25 per MTok
        },
        "sonnet": {
            "input": 3.0 / 1_000_000,
            "output": 15.0 / 1_000_000
        },
        "opus": {
            "input": 15.0 / 1_000_000,
            "output": 75.0 / 1_000_000
        }
    }

    if model not in pricing:
        raise ValueError(f"未知のモデル: {model}")

    cost = (
        input_tokens * pricing[model]["input"] +
        output_tokens * pricing[model]["output"]
    )

    return cost

# 実行例
cost = calculate_cost(
    model="sonnet",
    input_tokens=1000,
    output_tokens=500
)
print(f"コスト: ${cost:.4f}")
```

**使用場面**
- 予算管理
- モデル選択の最適化
- スケーラビリティの評価

### 4. スループット（Throughput）

**定義**
単位時間当たりの処理タスク数。

**測定方法**

```python
def measure_throughput(func, tasks: list, duration_seconds: int) -> dict:
    """スループットを測定"""
    start_time = time.time()
    processed = 0

    for task in tasks:
        if time.time() - start_time >= duration_seconds:
            break
        func(task)
        processed += 1

    elapsed = time.time() - start_time
    throughput = processed / elapsed if elapsed > 0 else 0

    return {
        "processed": processed,
        "elapsed_seconds": elapsed,
        "throughput_per_second": throughput,
        "throughput_per_minute": throughput * 60
    }
```

**使用場面**
- 大量データ処理
- システムの容量計画
- 並列化の効果測定

## テスト戦略

### 1. 単体テスト（Unit Testing）

**概要**
個別のコンポーネント（エージェント、ツール、関数）をテストする。

**実装例**

```python
import unittest

class TestSentimentAnalyzer(unittest.TestCase):
    def setUp(self):
        """各テストの前に実行"""
        self.analyzer = SentimentAnalyzer()

    def test_positive_sentiment(self):
        """ポジティブな感情の検出"""
        text = "This product is amazing! I love it."
        result = self.analyzer.analyze(text)

        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["confidence"], 0.8)

    def test_negative_sentiment(self):
        """ネガティブな感情の検出"""
        text = "This is terrible. I hate it."
        result = self.analyzer.analyze(text)

        self.assertEqual(result["sentiment"], "negative")
        self.assertGreater(result["confidence"], 0.8)

    def test_neutral_sentiment(self):
        """中立的な感情の検出"""
        text = "The sky is blue."
        result = self.analyzer.analyze(text)

        self.assertEqual(result["sentiment"], "neutral")

    def test_empty_input(self):
        """空入力のハンドリング"""
        with self.assertRaises(ValueError):
            self.analyzer.analyze("")

if __name__ == "__main__":
    unittest.main()
```

**ベストプラクティス**
- 各コンポーネントを独立してテスト
- エッジケースをカバー
- モックを使用して外部依存を排除
- テストケースを明確に命名

### 2. 統合テスト（Integration Testing）

**概要**
複数のコンポーネントの連携をテストする。

**実装例**

```python
class TestCustomerSupportWorkflow(unittest.TestCase):
    def test_end_to_end_technical_support(self):
        """技術サポートのエンドツーエンドテスト"""
        # 入力
        ticket = "アプリがクラッシュします。エラーコード: 500"

        # ワークフロー実行
        result = customer_support_workflow(ticket)

        # 検証
        self.assertIn("category", result)
        self.assertEqual(result["category"], "technical")
        self.assertIn("response", result)
        self.assertIn("500", result["response"])  # エラーコードに言及している
        self.assertGreater(len(result["response"]), 50)  # 十分な詳細がある

    def test_routing_to_correct_handler(self):
        """正しいハンドラーへのルーティング"""
        test_cases = [
            ("請求について教えてください", "billing"),
            ("バグを見つけました", "technical"),
            ("使い方を教えてください", "how_to")
        ]

        for ticket, expected_category in test_cases:
            result = customer_support_workflow(ticket)
            self.assertEqual(
                result["category"],
                expected_category,
                f"'{ticket}'が正しく分類されませんでした"
            )
```

**ベストプラクティス**
- 実際のワークフローをテスト
- 複数のコンポーネント間のデータフローを検証
- エラー伝播をテスト

### 3. エンドツーエンドテスト（End-to-End Testing）

**概要**
システム全体を実際のユーザーシナリオでテストする。

**実装例**

```python
class TestResearchAgent(unittest.TestCase):
    def test_complete_research_workflow(self):
        """完全な調査ワークフロー"""
        # 実際のユーザー入力
        query = "2024年のAI技術のトレンドは何ですか？"

        # システム実行
        result = research_agent.process(query)

        # 品質検証
        self.assertIsNotNone(result)
        self.assertIn("answer", result)
        self.assertIn("sources", result)

        # コンテンツ検証
        answer = result["answer"]
        self.assertGreater(len(answer), 200)  # 十分な詳細
        self.assertIn("AI", answer)  # トピックに関連

        # ソース検証
        sources = result["sources"]
        self.assertGreaterEqual(len(sources), 3)  # 複数のソース
        for source in sources:
            self.assertIn("url", source)
            self.assertIn("summary", source)

        # メトリクス検証
        self.assertLess(result["latency_ms"], 30000)  # 30秒以内
        self.assertLess(result["cost"], 0.50)  # $0.50以下
```

**ベストプラクティス**
- 実際のユーザーシナリオを再現
- すべてのコンポーネントを統合
- パフォーマンスメトリクスを検証
- 外部依存（API）も含める

### 4. 回帰テスト（Regression Testing）

**概要**
変更後もシステムが正しく動作することを確認する。

**実装例**

```python
class RegressionTestSuite:
    def __init__(self):
        # 既知の良好な出力を保存
        self.baseline_results = load_baseline_results()

    def test_against_baseline(self, test_cases: list):
        """ベースラインと比較"""
        failures = []

        for test_case in test_cases:
            current_result = run_test_case(test_case)
            baseline_result = self.baseline_results.get(test_case["id"])

            if not baseline_result:
                # 新しいテストケース
                continue

            # 比較
            if not self.results_match(current_result, baseline_result):
                failures.append({
                    "test_case": test_case,
                    "current": current_result,
                    "baseline": baseline_result
                })

        return {
            "total": len(test_cases),
            "failures": len(failures),
            "failure_details": failures
        }

    def results_match(self, current, baseline):
        """結果が一致するか確認"""
        # 完全一致は求めず、主要なメトリクスで比較
        metrics = ["accuracy", "category", "sentiment"]

        for metric in metrics:
            if current.get(metric) != baseline.get(metric):
                return False

        # パフォーマンスの著しい劣化をチェック
        if current.get("latency_ms", 0) > baseline.get("latency_ms", 0) * 1.5:
            return False

        return True
```

**ベストプラクティス**
- ベースラインを定期的に更新
- 重要なメトリクスに焦点を当てる
- 許容範囲を定義（完全一致は不要）

## Before/After例

### 例1: 評価方法の改善

#### Before（評価なし）

```python
def generate_summary(text):
    summary = call_llm(f"以下のテキストを要約してください: {text}")
    return summary

# 問題点:
# - 品質を評価していない
# - 要約が適切か不明
# - 改善の指標がない
```

#### After（評価を追加）

```python
def generate_summary_with_evaluation(text):
    summary = call_llm(f"以下のテキストを要約してください: {text}")

    # 評価
    evaluation = evaluate_summary(summary, text)

    return {
        "summary": summary,
        "evaluation": evaluation,
        "quality_score": evaluation["overall_score"]
    }

def evaluate_summary(summary, original_text):
    # コードベース評価
    length_check = len(summary) < len(original_text) * 0.3  # 30%以下

    # モデルベース評価
    criteria = {
        "conciseness": {"description": "簡潔性", "weight": 0.3},
        "completeness": {"description": "重要情報の網羅性", "weight": 0.4},
        "readability": {"description": "読みやすさ", "weight": 0.3}
    }

    llm_eval = evaluate_with_llm(summary, criteria, original_text)

    return {
        "length_appropriate": length_check,
        "llm_evaluation": llm_eval,
        "overall_score": llm_eval["overall_score"]
    }

# 改善ポイント:
# - 品質を定量的に評価
# - 改善の指標を取得
# - 問題の早期発見
```

### 例2: テスト戦略の追加

#### Before（テストなし）

```python
def classify_ticket(ticket):
    prompt = f"以下のチケットを分類してください: {ticket}"
    category = call_llm(prompt)
    return category

# 問題点:
# - 動作を検証していない
# - エッジケースが不明
# - リグレッションを検出できない
```

#### After（包括的なテスト）

```python
def classify_ticket(ticket):
    prompt = f"以下のチケットを分類してください: {ticket}"
    category = call_llm(prompt)
    return category

# 単体テスト
class TestTicketClassifier(unittest.TestCase):
    def test_technical_classification(self):
        ticket = "アプリがクラッシュします"
        result = classify_ticket(ticket)
        self.assertEqual(result, "technical")

    def test_billing_classification(self):
        ticket = "請求額が間違っています"
        result = classify_ticket(ticket)
        self.assertEqual(result, "billing")

    def test_empty_ticket(self):
        with self.assertRaises(ValueError):
            classify_ticket("")

# 統合テスト
class TestTicketWorkflow(unittest.TestCase):
    def test_classification_to_handler(self):
        ticket = "アプリがクラッシュします"
        result = process_ticket(ticket)  # 分類→処理
        self.assertEqual(result["category"], "technical")
        self.assertIn("response", result)

# 改善ポイント:
# - 動作を体系的に検証
# - エッジケースをカバー
# - リグレッションを防止
```

## まとめ

### 評価とテストのベストプラクティス

1. **複数の評価方法を組み合わせる**: コードベース、モデルベース、人間評価
2. **重要なメトリクスを追跡**: 精度、レイテンシ、コスト、スループット
3. **包括的なテスト戦略**: 単体、統合、エンドツーエンド、回帰
4. **継続的な評価**: 開発サイクル全体で評価を実施
5. **ベースラインを確立**: 改善を測定可能にする

### チェックリスト

**評価**
- [ ] 評価方法を選択したか？（コードベース/モデルベース/人間）
- [ ] 評価基準を明確に定義したか？
- [ ] 重要なメトリクスを追跡しているか？
- [ ] ベースラインを確立したか？

**テスト**
- [ ] 単体テストを実装したか？
- [ ] 統合テストを実装したか？
- [ ] エンドツーエンドテストを実装したか？
- [ ] 回帰テストを実装したか？
- [ ] エッジケースをカバーしたか？

### 次のステップ

- アンチパターンと回避方法: [anti-patterns.md](anti-patterns.md)
- 本番運用のベストプラクティス: [production-best-practices.md](production-best-practices.md)
- ワークフローパターンの詳細: [workflow-patterns-detail.md](workflow-patterns-detail.md)
