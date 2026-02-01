# 構造化出力（Structured Output）

## 構造化出力とは

構造化出力とは、JSON SchemaやPydanticなどのスキーマ定義を使用して、LLMの出力を予測可能で型安全な形式に制約する技術である。

スキーマを定義することで、LLMは指定された構造に従ったデータを生成する。これにより、以下が実現される：

- **予測可能性**: 出力フォーマットが保証される
- **型安全性**: 型チェックとバリデーションが可能
- **パースの簡素化**: JSON文字列のパースエラーが削減される
- **統合の容易性**: 生成されたデータを直接APIやデータベースに使用できる

### 主なユースケース

**データ抽出**
非構造化テキストから構造化データを抽出する。例：顧客フィードバックから製品名、評価、カテゴリを抽出。

**構造化分類**
事前定義されたカテゴリへの分類。例：問い合わせを「技術サポート」「請求」「一般質問」に分類。

**エージェントワークフロー**
ツールやAPI呼び出しのための正確な入力生成。例：検索クエリ、データベースクエリ、関数パラメータの生成。

## なぜ重要か

**予測可能性と信頼性**
スキーマがない場合、LLMの出力フォーマットは不安定である。構造化出力により、一貫した形式が保証される。

**型安全性**
スキーマ定義により、型チェックとバリデーションが実装時に実行される。実行時エラーを削減できる。

**エラー削減**
JSONパースエラー、欠損フィールド、不正な型などの問題を事前に防止できる。

**パース処理の簡素化**
文字列操作や正規表現による出力のパースが不要になる。生成されたデータをそのまま使用できる。

## 主要な選択肢

### Pydantic（Python）

**概要**
Pythonの型アノテーションベースのデータバリデーションライブラリ。LLM出力のスキーマ定義に広く使用される。

**特徴**
- Pythonの型ヒントを使用した直感的なスキーマ定義
- 強力なバリデーション機能（カスタムバリデータ、field_validator）
- IDE補完とLinterサポート
- JSON SchemaへのシリアライズとOpenAPI統合
- aliasによるフィールド名の柔軟な変換（camelCase対応など）

**適用場面**
- Python環境でのLLMアプリケーション開発
- 型安全性と開発者体験を重視する場合
- バリデーションロジックが複雑な場合

### Zod（TypeScript）

**概要**
TypeScript用のスキーマ宣言とバリデーションライブラリ。型推論が強力である。

**特徴**
- TypeScript型システムとの完全な統合
- 型推論による開発者体験の向上
- ランタイムバリデーション
- 詳細なエラーメッセージ

**適用場面**
- TypeScript環境でのLLMアプリケーション開発
- フロントエンドとバックエンドでスキーマを共有する場合
- 型安全性を最優先する場合

### JSON Schema（言語非依存）

**概要**
言語非依存のスキーマ定義標準。OpenAPIなどの仕様で広く使用される。

**特徴**
- 言語に依存しない移植性
- 標準仕様に基づく互換性
- OpenAPIやSwaggerとの統合

**適用場面**
- 複数の言語間でスキーマを共有する場合
- 標準仕様への準拠が必要な場合
- レガシーシステムとの統合

### 選択基準

| 基準 | Pydantic | Zod | JSON Schema |
|------|----------|-----|-------------|
| 開発言語 | Python | TypeScript | 言語非依存 |
| 型安全性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| IDE補完 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| バリデーション | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 学習曲線 | 低い | 低い | 中程度 |
| 移植性 | 低い | 低い | 高い |

## 本プロジェクトの実装例

本プロジェクトでは、Pydanticベースの構造化出力を実装している（コミット7553064）。

### 実装ファイル

**スキーマ定義**
- `backend/app/interfaces/schemas/travel_guide.py`: 旅行ガイド用スキーマ（複雑なネスト構造の実例）
- `backend/app/interfaces/schemas/reflection.py`: 振り返りパンフレット用スキーマ

**クライアント実装**
- `backend/app/infrastructure/ai/gemini_client.py:145-239`: `generate_content_with_schema`メソッド

### 実装の特徴

**Pydanticによる型安全性**
```python
class HistoricalEventSchema(BaseModel):
    year: int
    event: str
    significance: str
    related_spots: list[str] = Field(..., alias="relatedSpots")
```

**field_validatorによるカスタムバリデーション**
```python
@field_validator("plan_id")
@classmethod
def validate_not_empty(cls, value: str) -> str:
    if not value.strip():
        raise ValueError("must not be empty")
    return value
```

**aliasによるcamelCase対応**
```python
plan_id: str = Field(..., alias="planId")
model_config = {"populate_by_name": True}
```

**複雑なネスト構造のサポート**
```python
class TravelGuideResponse(BaseModel):
    timeline: list[HistoricalEventSchema]
    spot_details: list[SpotDetailSchema]
    checkpoints: list[CheckpointSchema]
```

### 学習推奨

実装の詳細を理解するには、以下のファイルを参照すること：

1. `backend/app/interfaces/schemas/travel_guide.py`: 複雑なネスト構造の実例
2. `backend/app/infrastructure/ai/gemini_client.py`: クライアント実装（特に`generate_content_with_schema`メソッド）
3. `backend/app/interfaces/schemas/reflection.py`: バリデーション戦略の実例

## ベストプラクティス

### スキーマ設計

**シンプルに保つ**
- 必要最小限のフィールドのみ定義する
- ネスト階層は3-4階層までに抑える
- 過度に厳格な制約を避ける

**明確なフィールド名**
- フィールド名は自己説明的にする
- aliasを使用してAPIとの命名規則の違いを吸収する
- 一貫した命名規則を使用する

### バリデーション

**必要最小限のバリデーション**
- LLMの柔軟性を損なう過度なバリデーションを避ける
- ビジネスロジックに必須の制約のみ実装する
- バリデーションエラー時には明確なメッセージを提供する

**早期失敗**
- バリデーションエラーは即座に検出する
- エラーの原因を明確にログに記録する

### エラーハンドリング

**グレースフルデグラデーション**
- スキーマ生成失敗時のフォールバック戦略を実装する
- エラーログを詳細に記録する
- ユーザーに分かりやすいエラーメッセージを提供する

### ワークフローパターンでの活用

**プロンプト連鎖**
各ステップの出力をスキーマで定義し、次のステップの入力として使用する。

**ルーティング**
分類結果をスキーマで定義し、ルーティングロジックで使用する。

**並列化**
複数のタスクの出力をスキーマで統一し、統合処理を簡素化する。

**オーケストレーター・ワーカー**
オーケストレーターの計画とワーカーの結果をスキーマで定義し、調整を容易にする。

**評価者・最適化者**
評価結果をスキーマで定義し、改善サイクルを明確にする。

## 公式ドキュメント

### Google Gemini Structured Output
- [Gemini API - Structured Output](https://ai.google.dev/gemini-api/docs/structured-output)
  - Gemini APIでの構造化出力の実装方法
  - JSON modeとSchema modeの使い分け
  - ベストプラクティスと制約事項

### Pydantic
- [Pydantic公式ドキュメント](https://docs.pydantic.dev/)
  - スキーマ定義の基本
  - バリデーションとカスタムバリデータ
  - JSON SchemaエクスポートとOpenAPI統合

### Zod
- [Zod公式ドキュメント](https://zod.dev/)
  - TypeScriptでのスキーマ定義
  - 型推論とランタイムバリデーション
  - エラーハンドリング

### Claude API
- [Anthropic API - Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
  - Claude APIでの構造化出力とツール使用
  - スキーマ定義のベストプラクティス

### JSON Schema
- [JSON Schema公式サイト](https://json-schema.org/)
  - 言語非依存のスキーマ定義標準
  - OpenAPIとの統合
