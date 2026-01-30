# ユースケース別実装例

このドキュメントでは、6つの代表的なユースケースにおけるAI Agent設計の実装例を提供する。各例には、推奨されるワークフローパターン、具体的な実装、考慮事項を含む。

## 1. コード生成エージェント

### ユースケース

ユーザーの要求に基づいて、高品質なコードを生成し、テストとドキュメントも提供する。

### 推奨パターン

プロンプト連鎖 + 評価者・最適化者

### 実装例

```python
def code_generation_agent(requirements: str) -> dict:
    """コード生成エージェント"""

    # ステップ1: 要件分析
    analysis = analyze_requirements(requirements)

    # ステップ2: コード生成
    code = generate_code(analysis)

    # ステップ3: テスト生成
    tests = generate_tests(code, analysis)

    # ステップ4: 評価と改善
    evaluation = evaluate_code(code, tests, analysis)

    if evaluation["needs_improvement"]:
        code = improve_code(code, evaluation["suggestions"])
        tests = update_tests(tests, code)

    # ステップ5: ドキュメント生成
    documentation = generate_documentation(code, analysis)

    return {
        "code": code,
        "tests": tests,
        "documentation": documentation,
        "evaluation": evaluation
    }

def analyze_requirements(requirements: str) -> dict:
    """要件を分析"""
    prompt = f"""
以下の要件を分析し、実装の詳細を決定してください。

要件: {requirements}

以下のJSON形式で出力してください:
{{
  "functionality": "主要な機能",
  "input_output": {{"input": "入力の型", "output": "出力の型"}},
  "constraints": ["制約1", "制約2", ...],
  "edge_cases": ["エッジケース1", "エッジケース2", ...]
}}
"""
    result = call_llm(prompt, temperature=0.2)
    return json.loads(result)

def generate_code(analysis: dict) -> str:
    """コードを生成"""
    prompt = f"""
以下の分析に基づいて、Pythonコードを生成してください。

分析結果:
{json.dumps(analysis, indent=2)}

要件:
- 型ヒントを使用
- docstringを含める
- エッジケースを処理
- クリーンで読みやすいコード
"""
    code = call_llm(prompt, temperature=0.3, tools=["run_code"])
    return code

def generate_tests(code: str, analysis: dict) -> str:
    """テストを生成"""
    prompt = f"""
以下のコードのpytestテストを生成してください。

コード:
{code}

エッジケース:
{analysis["edge_cases"]}

すべてのエッジケースをカバーするテストを含めてください。
"""
    tests = call_llm(prompt, temperature=0.3)
    return tests

def evaluate_code(code: str, tests: str, analysis: dict) -> dict:
    """コードを評価"""
    # テスト実行
    test_result = run_tests(tests)

    # コード品質評価
    quality_prompt = f"""
以下のコードを評価してください。

コード:
{code}

評価基準:
- 正確性: 要件を満たしているか
- 読みやすさ: コードは理解しやすいか
- 効率性: アルゴリズムは効率的か
- 保守性: 将来の変更が容易か

テスト結果: {"成功" if test_result["success"] else "失敗"}

評価と改善提案を提供してください。
"""
    evaluation = call_llm(quality_prompt, temperature=0.2)

    return {
        "needs_improvement": not test_result["success"] or "改善" in evaluation,
        "test_results": test_result,
        "evaluation": evaluation,
        "suggestions": extract_suggestions(evaluation)
    }
```

### 考慮事項

- **セキュリティ**: 生成されたコードの安全性を検証
- **実行環境**: サンドボックス内でコードを実行
- **反復改善**: テストが失敗した場合は自動的に修正
- **ドキュメント**: コードの使用方法を明確に説明

## 2. データ分析エージェント

### ユースケース

データセットを分析し、インサイトを抽出してレポートを生成する。

### 推奨パターン

プロンプト連鎖 + 並列化

### 実装例

```python
import asyncio

async def data_analysis_agent(dataset: str, questions: list) -> dict:
    """データ分析エージェント"""

    # ステップ1: データの理解
    data_summary = analyze_data_structure(dataset)

    # ステップ2: 複数の分析を並列実行
    analysis_tasks = [
        perform_statistical_analysis(dataset, data_summary),
        identify_patterns(dataset, data_summary),
        detect_anomalies(dataset, data_summary),
        answer_questions(dataset, questions, data_summary)
    ]

    results = await asyncio.gather(*analysis_tasks)

    statistical_analysis, patterns, anomalies, answers = results

    # ステップ3: インサイトの統合
    insights = integrate_insights(
        statistical_analysis,
        patterns,
        anomalies,
        answers
    )

    # ステップ4: レポート生成
    report = generate_analysis_report(insights, dataset)

    return {
        "summary": data_summary,
        "insights": insights,
        "report": report
    }

def analyze_data_structure(dataset: str) -> dict:
    """データ構造を分析"""
    prompt = f"""
以下のデータセットを分析してください。

データ:
{dataset[:1000]}...  # 最初の1000文字

以下を特定してください:
- データの型（CSV、JSON、など）
- カラム/フィールド名
- データサイズ
- 欠損値の有無
"""
    result = call_llm(prompt, temperature=0.2)
    return parse_data_summary(result)

async def perform_statistical_analysis(dataset: str, summary: dict):
    """統計分析を実行"""
    prompt = f"""
以下のデータの統計分析を実行してください。

データ構造:
{summary}

実行する分析:
- 基本統計量（平均、中央値、標準偏差）
- 分布の分析
- 相関分析
"""
    analysis = await call_llm_async(
        prompt,
        tools=["run_code"],
        temperature=0.2
    )
    return analysis

async def identify_patterns(dataset: str, summary: dict):
    """パターンを特定"""
    prompt = f"""
以下のデータからパターンやトレンドを特定してください。

データ構造:
{summary}

特定するパターン:
- 時系列トレンド
- カテゴリ間の関係
- 季節性パターン
"""
    patterns = await call_llm_async(prompt, temperature=0.3)
    return patterns
```

### 考慮事項

- **データプライバシー**: 機密データを適切に処理
- **大規模データ**: サンプリングやチャンク化を活用
- **可視化**: グラフやチャートを生成
- **解釈可能性**: 分析結果を分かりやすく説明

## 3. カスタマーサポートエージェント

### ユースケース

顧客の問い合わせに対して、適切な回答やアクションを提供する。

### 推奨パターン

ルーティング + プロンプト連鎖

### 実装例

```python
def customer_support_agent(ticket: str, customer_id: str) -> dict:
    """カスタマーサポートエージェント"""

    # ステップ1: チケット分類
    category = classify_ticket(ticket)

    # ステップ2: 顧客情報取得
    customer_info = get_customer_info(customer_id)

    # ステップ3: カテゴリ別処理
    handlers = {
        "technical": handle_technical_issue,
        "billing": handle_billing_inquiry,
        "account": handle_account_issue,
        "general": handle_general_inquiry
    }

    handler = handlers.get(category, handle_general_inquiry)
    response = handler(ticket, customer_info)

    # ステップ4: 回答の品質チェック
    quality = check_response_quality(response, ticket)

    if quality["needs_improvement"]:
        response = improve_response(response, quality["suggestions"])

    # ステップ5: フォローアップアクション
    actions = determine_followup_actions(ticket, category, response)

    return {
        "category": category,
        "response": response,
        "actions": actions,
        "quality_score": quality["score"]
    }

def classify_ticket(ticket: str) -> str:
    """チケットを分類"""
    prompt = f"""
以下のカスタマーサポートチケットを分類してください。

チケット: {ticket}

カテゴリ:
- technical: 技術的な問題（バグ、エラー、機能不具合）
- billing: 請求に関する問い合わせ
- account: アカウント関連（パスワード、設定）
- general: 一般的な質問

カテゴリ名のみを返してください。
"""
    category = call_llm(prompt, model="haiku", temperature=0.1)
    return category.strip()

def handle_technical_issue(ticket: str, customer_info: dict) -> str:
    """技術的問題を処理"""
    # ステップ1: 問題診断
    diagnosis = diagnose_issue(ticket, customer_info)

    # ステップ2: 既知の問題を検索
    known_solutions = search_knowledge_base(diagnosis)

    # ステップ3: 解決策を提供
    prompt = f"""
以下の技術的問題に対する解決策を提供してください。

問題: {ticket}
診断結果: {diagnosis}
既知の解決策: {known_solutions}
顧客情報: プラン={customer_info["plan"]}, バージョン={customer_info["version"]}

明確で段階的な解決手順を提供してください。
"""
    solution = call_llm(
        prompt,
        tools=["search_documentation", "run_code"],
        temperature=0.3
    )
    return solution

def handle_billing_inquiry(ticket: str, customer_info: dict) -> str:
    """請求問い合わせを処理"""
    # 請求情報を取得
    billing_info = get_billing_details(customer_info["id"])

    prompt = f"""
以下の請求に関する問い合わせに回答してください。

問い合わせ: {ticket}
顧客ID: {customer_info["id"]}
請求情報: {billing_info}

明確で丁寧な説明を提供してください。
"""
    response = call_llm(prompt, temperature=0.2)
    return response
```

### 考慮事項

- **応答時間**: 迅速な回答を提供
- **一貫性**: 同じ質問には同じ回答
- **エスカレーション**: 複雑な問題は人間にエスカレート
- **満足度追跡**: 顧客満足度を測定

## 4. コンテンツ生成エージェント

### ユースケース

トピックに基づいて、高品質なコンテンツ（記事、ブログ投稿、マーケティングコピーなど）を生成する。

### 推奨パターン

プロンプト連鎖 + 評価者・最適化者

### 実装例

```python
def content_generation_agent(
    topic: str,
    content_type: str,
    brand_guidelines: dict,
    target_audience: str
) -> dict:
    """コンテンツ生成エージェント"""

    # ステップ1: リサーチ
    research = conduct_research(topic)

    # ステップ2: アウトライン作成
    outline = create_outline(topic, content_type, research, target_audience)

    # ステップ3: コンテンツ生成
    content = generate_content(outline, brand_guidelines, target_audience)

    # ステップ4: 評価と改善
    max_iterations = 3
    for iteration in range(max_iterations):
        evaluation = evaluate_content(content, brand_guidelines, outline)

        if evaluation["meets_criteria"]:
            break

        content = refine_content(content, evaluation["feedback"])

    # ステップ5: SEO最適化
    seo_optimized = optimize_for_seo(content, topic)

    return {
        "content": seo_optimized,
        "outline": outline,
        "research_sources": research["sources"],
        "quality_score": evaluation["score"]
    }

def conduct_research(topic: str) -> dict:
    """トピックをリサーチ"""
    prompt = f"""
以下のトピックについてリサーチしてください。

トピック: {topic}

収集する情報:
- 最新のトレンドとニュース
- 統計データ
- 専門家の意見
- 関連する事例
"""
    research = call_llm(
        prompt,
        tools=["search_web", "fetch_url"],
        temperature=0.3
    )

    return {
        "content": research,
        "sources": extract_sources(research)
    }

def create_outline(
    topic: str,
    content_type: str,
    research: dict,
    target_audience: str
) -> dict:
    """アウトラインを作成"""
    prompt = f"""
以下の情報に基づいて、{content_type}のアウトラインを作成してください。

トピック: {topic}
ターゲットオーディエンス: {target_audience}
リサーチ結果: {research["content"]}

アウトラインには以下を含めてください:
- 魅力的な導入
- 主要なポイント（3-5個）
- 各ポイントのサポート情報
- 強力な結論
"""
    outline = call_llm(prompt, temperature=0.5)
    return parse_outline(outline)

def generate_content(
    outline: dict,
    brand_guidelines: dict,
    target_audience: str
) -> str:
    """コンテンツを生成"""
    prompt = f"""
以下のアウトラインに基づいてコンテンツを執筆してください。

アウトライン:
{json.dumps(outline, indent=2)}

ブランドガイドライン:
- トーン: {brand_guidelines["tone"]}
- スタイル: {brand_guidelines["style"]}
- 避けるべき表現: {brand_guidelines["avoid"]}

ターゲットオーディエンス: {target_audience}

魅力的で読みやすいコンテンツを作成してください。
"""
    content = call_llm(prompt, temperature=0.7)
    return content

def evaluate_content(
    content: str,
    brand_guidelines: dict,
    outline: dict
) -> dict:
    """コンテンツを評価"""
    criteria = {
        "brand_alignment": {
            "description": "ブランドガイドラインとの一貫性",
            "weight": 0.3
        },
        "engagement": {
            "description": "読者を引き付ける魅力",
            "weight": 0.3
        },
        "clarity": {
            "description": "明確性と理解しやすさ",
            "weight": 0.2
        },
        "completeness": {
            "description": "アウトラインのカバー率",
            "weight": 0.2
        }
    }

    evaluation = evaluate_with_llm(content, criteria)

    return {
        "meets_criteria": evaluation["overall_score"] >= 80,
        "score": evaluation["overall_score"],
        "feedback": evaluation.get("suggestions", [])
    }
```

### 考慮事項

- **ブランド一貫性**: ブランドガイドラインを厳守
- **オリジナリティ**: 盗作を避ける
- **SEO**: 検索エンジン最適化
- **読みやすさ**: ターゲットオーディエンスに適した文体

## 5. 研究・調査エージェント

### ユースケース

複雑なトピックについて包括的な調査を行い、詳細なレポートを生成する。

### 推奨パターン

オーケストレーター・ワーカー + 並列化

### 実装例

```python
async def research_agent(research_question: str) -> dict:
    """研究・調査エージェント"""

    # ステップ1: リサーチ計画を立てる
    plan = create_research_plan(research_question)

    # ステップ2: 計画に基づいてワーカーを実行
    results = await execute_research_plan(plan)

    # ステップ3: 結果を統合
    integrated_findings = integrate_research_results(results)

    # ステップ4: レポートを生成
    report = generate_research_report(research_question, integrated_findings)

    return {
        "question": research_question,
        "findings": integrated_findings,
        "report": report,
        "sources": collect_sources(results)
    }

def create_research_plan(question: str) -> dict:
    """リサーチ計画を立てる（オーケストレーター）"""
    prompt = f"""
以下のリサーチ質問に答えるための調査計画を立ててください。

質問: {question}

利用可能なリサーチ手法:
- literature_search: 学術文献の検索
- web_research: Web情報の収集
- data_analysis: データ分析
- expert_consultation: 専門家の意見収集

JSON形式で計画を出力してください:
{{
  "subtopics": ["サブトピック1", "サブトピック2", ...],
  "research_tasks": [
    {{
      "method": "手法名",
      "focus": "焦点",
      "priority": "high/medium/low"
    }},
    ...
  ]
}}
"""
    result = call_llm(prompt, model="sonnet", temperature=0.3)
    return json.loads(result)

async def execute_research_plan(plan: dict) -> list:
    """リサーチ計画を実行"""
    # 優先度の高いタスクを並列実行
    high_priority_tasks = [
        task for task in plan["research_tasks"]
        if task["priority"] == "high"
    ]

    async_tasks = [
        execute_research_task(task)
        for task in high_priority_tasks
    ]

    high_priority_results = await asyncio.gather(*async_tasks)

    # 中・低優先度タスク
    other_tasks = [
        task for task in plan["research_tasks"]
        if task["priority"] != "high"
    ]

    other_results = []
    for task in other_tasks:
        result = await execute_research_task(task)
        other_results.append(result)

    return high_priority_results + other_results

async def execute_research_task(task: dict):
    """個別のリサーチタスクを実行（ワーカー）"""
    method = task["method"]

    if method == "literature_search":
        return await search_literature(task["focus"])
    elif method == "web_research":
        return await search_web_comprehensive(task["focus"])
    elif method == "data_analysis":
        return await analyze_relevant_data(task["focus"])
    elif method == "expert_consultation":
        return await consult_experts(task["focus"])
```

### 考慮事項

- **情報源の信頼性**: 信頼できる情報源を優先
- **最新性**: 最新の情報を含める
- **バイアス**: 複数の視点を取り入れる
- **引用**: すべての情報源を適切に引用

## 6. タスク自動化エージェント

### ユースケース

定型業務や反復タスクを自動化する。

### 推奨パターン

プロンプト連鎖 + ルーティング

### 実装例

```python
def task_automation_agent(task_description: str) -> dict:
    """タスク自動化エージェント"""

    # ステップ1: タスク理解
    task_analysis = analyze_task(task_description)

    # ステップ2: タスクタイプに応じたルーティング
    task_type = task_analysis["type"]

    automation_handlers = {
        "data_processing": automate_data_processing,
        "email_management": automate_email_management,
        "report_generation": automate_report_generation,
        "file_organization": automate_file_organization
    }

    handler = automation_handlers.get(task_type)

    if not handler:
        return {"error": f"未対応のタスクタイプ: {task_type}"}

    # ステップ3: 自動化スクリプト生成
    automation_script = handler(task_analysis)

    # ステップ4: スクリプト検証
    validation = validate_automation_script(automation_script)

    if not validation["is_safe"]:
        return {
            "error": "安全性の問題が検出されました",
            "issues": validation["issues"]
        }

    # ステップ5: スクリプト実行
    result = execute_automation(automation_script, task_analysis)

    return {
        "task": task_description,
        "automation_type": task_type,
        "result": result,
        "script": automation_script
    }

def analyze_task(description: str) -> dict:
    """タスクを分析"""
    prompt = f"""
以下のタスクを分析してください。

タスク: {description}

以下を特定してください:
- タスクタイプ（data_processing, email_management, report_generation, file_organization）
- 入力データの種類
- 期待される出力
- 実行頻度
- 必要なツール
"""
    analysis = call_llm(prompt, temperature=0.2)
    return parse_task_analysis(analysis)

def automate_data_processing(task_analysis: dict) -> str:
    """データ処理の自動化スクリプトを生成"""
    prompt = f"""
以下のデータ処理タスクを自動化するPythonスクリプトを生成してください。

タスク分析:
{json.dumps(task_analysis, indent=2)}

要件:
- エラーハンドリングを含める
- ログ出力を含める
- 実行可能なスクリプト
"""
    script = call_llm(prompt, temperature=0.3)
    return script
```

### 考慮事項

- **安全性**: 自動化スクリプトの安全性を検証
- **エラーハンドリング**: 堅牢なエラー処理
- **ログとモニタリング**: 実行状況を追跡
- **スケジューリング**: 定期実行の設定

## まとめ

### ユースケース別の選択ガイド

| ユースケース | 主要パターン | 重点領域 |
|------------|------------|---------|
| コード生成 | プロンプト連鎖 + 評価者・最適化者 | 品質、テスト |
| データ分析 | プロンプト連鎖 + 並列化 | インサイト、可視化 |
| カスタマーサポート | ルーティング + プロンプト連鎖 | 応答時間、精度 |
| コンテンツ生成 | プロンプト連鎖 + 評価者・最適化者 | ブランド一貫性、品質 |
| 研究・調査 | オーケストレーター・ワーカー + 並列化 | 包括性、信頼性 |
| タスク自動化 | プロンプト連鎖 + ルーティング | 安全性、信頼性 |

### 次のステップ

- Before/After改善例: [before-after-examples.md](before-after-examples.md)
- ワークフローパターン実装: [workflow-patterns.md](workflow-patterns.md)
- アーキテクチャ原則: [../references/architecture-principles.md](../references/architecture-principles.md)
