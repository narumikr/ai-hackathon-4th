---
name: api-design
description: RESTful API設計のベストプラクティスを適用してAPI設計を改善する。ユーザーが「APIを設計して」「API仕様をレビューして」「RESTful APIのベストプラクティスを教えて」と依頼した時、またはAPI設計について質問した時に使用する。エンドポイント設計、HTTPメソッドの選択、ステータスコードの使用、エラーハンドリング、バージョニングなどの観点からAPI設計を支援する。
---

# RESTful API設計 ベストプラクティス

## 概要

RESTful API設計は、開発者体験、保守性、拡張性を左右する重要な要素である。効果的なAPI設計は、以下を実現する:

- **一貫性のある開発者体験**: 直感的で予測可能なインターフェース
- **保守性の向上**: 明確な設計原則に基づく変更容易性
- **拡張性の確保**: 下位互換性を保ちながら機能を追加できる設計

### 対象範囲

- REST API（HTTP/HTTPSベース）
- JSON形式のリクエスト/レスポンス
- FastAPI、Express.js、Spring Bootなど一般的なフレームワーク

## 基本原則

効果的なRESTful API設計の基本原則:

### 1. リソース指向設計

APIはリソース（データやオブジェクト）を中心に設計する。URIはリソースを識別し、HTTPメソッドはリソースに対する操作を表現する。

### 2. ステートレス性

各リクエストは独立しており、サーバーはリクエスト間でクライアント状態を保持しない。必要な情報はすべてリクエストに含める。

### 3. HTTPメソッドの正しい使用

HTTPメソッドのセマンティクス（GET、POST、PUT、PATCH、DELETE）を正しく理解し、適切に使用する。

### 4. 一貫性のある命名規則

リソース名、パラメータ名、フィールド名に一貫したケーススタイルと命名パターンを使用する。

### 5. 適切なステータスコードの使用

HTTPステータスコードを正しく使用し、APIの振る舞いを明確に伝える。

## コアベストプラクティス（優先順位順）

### 1. リソース設計とURI構造

#### 基本ルール

- **複数形の名詞を使用**: `/api/v1/travel-plans`（○）、`/api/v1/travel-plan`（×）
- **階層構造を表現**: `/api/v1/travel-plans/{plan_id}/guides`
- **動詞を避ける**: `/api/v1/get-travel-plan`（×）、`/api/v1/travel-plans/{plan_id}`（○）
- **ケバブケースを使用**: `travel-plans`（○）、`travel_plans`（△）、`travelPlans`（×）

#### Before/After例

**Before**（悪い設計）:
```
POST /api/getTravelPlan
GET /api/createTravelPlan
DELETE /api/deleteTravelPlan?id=123
```

**After**（良い設計）:
```
GET /api/v1/travel-plans/{plan_id}
POST /api/v1/travel-plans
DELETE /api/v1/travel-plans/{plan_id}
```

**改善ポイント**:
- リソース名を複数形の名詞に変更
- HTTPメソッドで操作を表現（URIから動詞を削除）
- パスパラメータで個別リソースを識別

#### サブリソースの扱い

**ネストを適切に使用**:
```
GET /api/v1/travel-plans/{plan_id}/guides        # 旅行計画に関連するガイド一覧
GET /api/v1/travel-plans/{plan_id}/reflections   # 旅行計画に関連する振り返り
```

**過度なネストは避ける**（2階層まで推奨）:
```
❌ /api/v1/users/{user_id}/travel-plans/{plan_id}/guides/{guide_id}/sections/{section_id}
✅ /api/v1/guides/{guide_id}/sections/{section_id}
```

### 2. HTTPメソッドの使用

各HTTPメソッドの正しい使用方法と冪等性の理解。

#### メソッド一覧

| メソッド | 用途 | 冪等性 | リクエストボディ | レスポンスボディ |
|---------|------|--------|----------------|----------------|
| GET | リソース取得 | ✅ | なし | あり |
| POST | リソース作成 | ❌ | あり | あり（作成されたリソース） |
| PUT | リソース全体更新 | ✅ | あり | あり（更新後のリソース） |
| PATCH | リソース部分更新 | △ | あり | あり（更新後のリソース） |
| DELETE | リソース削除 | ✅ | なし | なし（204）または削除結果 |

#### Before/After例

**Before**（悪い設計）:
```python
@router.get("/travel-plans/create")  # GETでリソース作成
def create_travel_plan(title: str, destination: str):
    ...
```

**After**（良い設計）:
```python
@router.post("/travel-plans", status_code=status.HTTP_201_CREATED)
def create_travel_plan(request: CreateTravelPlanRequest):
    ...
```

**改善ポイント**:
- リソース作成はPOSTを使用
- 201 Createdステータスを返す
- リクエストボディでデータを受け取る

### 3. ステータスコードとエラーハンドリング

適切なHTTPステータスコードを使用し、エラーレスポンスを構造化する。

#### 主要なステータスコード

**成功系（2xx）**:
- `200 OK`: GET、PUT、PATCH成功
- `201 Created`: POST成功（Locationヘッダー推奨）
- `204 No Content`: DELETE成功、レスポンスボディなし

**クライアントエラー（4xx）**:
- `400 Bad Request`: バリデーションエラー
- `401 Unauthorized`: 認証エラー
- `403 Forbidden`: 認可エラー
- `404 Not Found`: リソースが見つからない
- `409 Conflict`: リソース競合

**サーバーエラー（5xx）**:
- `500 Internal Server Error`: サーバー内部エラー
- `503 Service Unavailable`: サービス利用不可

#### エラーレスポンスの構造化

**Before**（悪い設計）:
```json
"Travel plan not found"
```

**After**（良い設計）:
```json
{
  "error": {
    "code": "TRAVEL_PLAN_NOT_FOUND",
    "message": "Travel plan not found: plan_123",
    "details": {
      "plan_id": "plan_123"
    }
  }
}
```

**改善ポイント**:
- エラーコード、メッセージ、詳細情報を含む
- 機械的に処理可能な構造
- デバッグに必要な情報を提供

#### プロジェクト実装例

```python
# backend/app/interfaces/api/v1/travel_plans.py:174-178
except TravelPlanNotFoundError as e:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Travel plan not found: {plan_id}",
    ) from e
```

### 4. バージョニング戦略

API仕様の変更に備え、明確なバージョニング戦略を採用する。

#### URLバージョニング（推奨）

```
/api/v1/travel-plans
/api/v2/travel-plans
```

**メリット**:
- 明示的でわかりやすい
- ブラウザで直接アクセス可能
- ドキュメント化が容易

#### 下位互換性の維持

**破壊的変更の例**:
- 既存フィールドの削除
- 既存フィールドの型変更
- 必須フィールドの追加

**非破壊的変更の例**:
- 新しいオプションフィールドの追加
- 新しいエンドポイントの追加
- エラーメッセージの改善

**Before/After例**:

**Before**（破壊的変更）:
```json
// v1
{"status": "planning"}

// v2（破壊的）
{"status": {"value": "planning", "updatedAt": "2025-01-30T10:00:00Z"}}
```

**After**（非破壊的変更）:
```json
// v1
{"status": "planning"}

// v2（後方互換）
{"status": "planning", "statusDetail": {"value": "planning", "updatedAt": "2025-01-30T10:00:00Z"}}
```

#### プロジェクト実装例

```python
# backend/main.py:58-61
app.include_router(travel_plans.router, prefix="/api/v1")
app.include_router(travel_guides.router, prefix="/api/v1")
app.include_router(reflections.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
```

## クイックチェックリスト

API設計時に確認する項目:

- [ ] リソース名は複数形の名詞か?
- [ ] URIに動詞を含めていないか?
- [ ] HTTPメソッドは適切か（GET/POST/PUT/PATCH/DELETE）?
- [ ] 成功時のステータスコードは適切か（200/201/204）?
- [ ] エラー時のステータスコードは適切か（400/401/403/404/409/500）?
- [ ] エラーレスポンスは構造化されているか?
- [ ] バージョニング戦略は明確か（/api/v1/）?
- [ ] ページネーションやフィルタリングは必要か?
- [ ] セキュリティ対策は十分か（認証、認可、入力バリデーション）?
- [ ] APIドキュメントは最新か（OpenAPI仕様など）?

## 詳細リファレンス

より詳細な情報は以下のファイルを参照:

- **リソース設計**: `references/resource-design.md`
  - URI設計の詳細ルール
  - リレーションシップの表現
  - 命名規則の詳細

- **HTTPメソッドとステータスコード**: `references/http-methods-and-status-codes.md`
  - 各HTTPメソッドの詳細
  - ステータスコードの使い分け
  - エラーレスポンス設計

- **ページネーション・フィルタリング・ソート**: `references/pagination-filtering-sorting.md`
  - ページネーション手法
  - フィルタリングパラメータ設計
  - ソート機能の実装

- **バージョニングと互換性**: `references/versioning-and-compatibility.md`
  - バージョニング手法の比較
  - 下位互換性の維持戦略
  - マイグレーション計画

- **認証とセキュリティ**: `references/authentication-and-security.md`
  - 認証方式（JWT、OAuth 2.0）
  - セキュリティヘッダー
  - レート制限

- **アンチパターン**: `references/anti-patterns.md`
  - 避けるべきパターン
  - よくある失敗例

## 実装例

実際の使用例は以下のファイルを参照:

- **改善前後の比較**: `examples/before-after-examples.md`
  - CRUD API設計の改善
  - エラーハンドリングの改善
  - ページネーションの実装
  - リレーションシップの表現
  - バージョニングの導入

- **ドメイン別パターン**: `examples/domain-specific-examples.md`
  - ユーザー管理API
  - Eコマース注文API
  - ブログ/CMS API
  - 旅行計画API（プロジェクト関連）

## 使用方法

このスキルは以下の場合に自動的に呼び出される:

- ユーザーが「APIを設計して」と依頼した時
- 「API仕様をレビューして」と要求した時
- 「RESTful APIのベストプラクティスを教えて」と述べた時
- API設計について質問した時

手動で呼び出す場合: `/api-design`

## API設計レビューの実践

ユーザーのAPI設計をレビューする際の手順:

1. **現在の設計を分析**: エンドポイント、HTTPメソッド、ステータスコード、エラーハンドリングを確認
2. **適用可能なベストプラクティスを特定**: 上記4つのコアプラクティスから選択
3. **改善版を提案**: Before/Afterを明示
4. **改善ポイントを説明**: なぜその変更が効果的かを説明
5. **必要に応じて詳細リファレンスを提供**: references/やexamples/を紹介

## 重要な注意事項

- **過度な最適化を避ける**: すべてのベストプラクティスを常に適用する必要はない
- **プロジェクト固有の規約を優先**: 既存の設計パターンと一貫性を保つ
- **実際のユースケースに基づく設計**: 理論よりも実際の使用シナリオを重視
- **段階的な改善**: 一度にすべてを変更するのではなく、優先順位をつけて改善
