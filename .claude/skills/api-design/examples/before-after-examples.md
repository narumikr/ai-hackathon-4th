# API設計改善例: Before/After

## 概要

実際のAPI設計における改善例を、Before/After形式で示す。各例には、問題点と改善ポイントを明記する。

## 例1: CRUD API設計

### Before（悪い設計）

```python
# エンドポイント定義
@router.get("/getTravelPlans")
def get_travel_plans(userId: str):
    ...

@router.post("/createTravelPlan")
def create_travel_plan(data: dict):
    ...

@router.get("/getTravelPlan")
def get_travel_plan(planId: str):
    ...

@router.post("/updateTravelPlan")
def update_travel_plan(planId: str, data: dict):
    ...

@router.post("/deleteTravelPlan")
def delete_travel_plan(planId: str):
    ...
```

**問題点**:
- URIに動詞を含めている（`getTravelPlans`, `createTravelPlan`など）
- すべての操作にGETまたはPOSTのみを使用
- HTTPメソッドのセマンティクスを無視
- パラメータ名がキャメルケース
- バージョニングなし
- ステータスコードの指定なし

### After（良い設計）

```python
# エンドポイント定義
@router.get(
    "",
    response_model=list[TravelPlanListResponse],
    summary="旅行計画一覧を取得",
)
def list_travel_plans(user_id: str):
    """ユーザーの旅行計画一覧を取得する"""
    ...

@router.post(
    "",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="旅行計画を作成",
)
def create_travel_plan(request: CreateTravelPlanRequest):
    """旅行計画を作成する"""
    ...

@router.get(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を取得",
)
def get_travel_plan(plan_id: str):
    """旅行計画を取得する"""
    ...

@router.put(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を更新",
)
def update_travel_plan(plan_id: str, request: UpdateTravelPlanRequest):
    """旅行計画を更新する"""
    ...

@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="旅行計画を削除",
)
def delete_travel_plan(plan_id: str):
    """旅行計画を削除する"""
    ...
```

**改善ポイント**:
- ✅ リソース名を複数形の名詞に変更（`/travel-plans`）
- ✅ HTTPメソッドで操作を表現（GET、POST、PUT、DELETE）
- ✅ URIから動詞を削除
- ✅ パスパラメータで個別リソースを識別（`/{plan_id}`）
- ✅ クエリパラメータをスネークケースに変更（`user_id`）
- ✅ 適切なステータスコードを指定（201、204）
- ✅ 型安全なリクエスト/レスポンススキーマを使用
- ✅ ドキュメント文字列を追加

## 例2: エラーハンドリング

### Before（悪い設計）

```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    plan = repository.find(plan_id)
    if not plan:
        # 常に200を返し、エラーメッセージを文字列で返す
        return "Travel plan not found"
    return plan
```

**レスポンス例**:
```
HTTP/1.1 200 OK
Content-Type: text/plain

Travel plan not found
```

**問題点**:
- エラー時も200 OKを返す
- エラーレスポンスが文字列のみ
- 機械的に処理できない
- エラーの詳細情報がない
- 例外を適切にハンドリングしていない

### After（良い設計）

```python
@router.get(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を取得",
    responses={
        404: {"description": "Travel plan not found"},
        400: {"description": "Invalid plan ID"},
    },
)
def get_travel_plan(plan_id: str):
    """旅行計画を取得する

    Args:
        plan_id: 旅行計画ID

    Returns:
        TravelPlanResponse: 旅行計画

    Raises:
        HTTPException: 旅行計画が見つからない（404）
    """
    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
```

**レスポンス例（404）**:
```json
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "detail": "Travel plan not found: plan_123"
}
```

**改善ポイント**:
- ✅ 適切なHTTPステータスコードを使用（404、400）
- ✅ 例外を型別にハンドリング
- ✅ エラーレスポンスがJSON形式で構造化されている
- ✅ エラーの詳細情報を含める（plan_id）
- ✅ OpenAPIドキュメントにエラーレスポンスを記載
- ✅ 例外チェーンを保持（`from e`）

**さらなる改善（RFC 7807準拠）**:

```python
# カスタムエラーレスポンススキーマ
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

# エンドポイント実装
@router.get("/{plan_id}", response_model=TravelPlanResponse)
def get_travel_plan(plan_id: str):
    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TRAVEL_PLAN_NOT_FOUND",
                "message": f"Travel plan not found: {plan_id}",
                "details": {"plan_id": plan_id}
            }
        ) from e
```

## 例3: ページネーションとフィルタリング

### Before（悪い設計）

```python
@router.get("/travel-plans")
def list_travel_plans():
    # すべての旅行計画を取得（パフォーマンス問題）
    plans = repository.find_all()
    return plans
```

**問題点**:
- ページネーション機能なし
- フィルタリング機能なし
- すべてのデータを一度に返す（パフォーマンス問題）
- データ量が増えるとレスポンスサイズが巨大化

### After（良い設計）

```python
@router.get(
    "",
    response_model=PaginatedTravelPlanResponse,
    summary="旅行計画一覧を取得",
)
def list_travel_plans(
    user_id: str | None = None,
    status: str | None = None,
    sort: str = "-created_at",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """旅行計画一覧を取得する

    Args:
        user_id: ユーザーIDでフィルタ（オプション）
        status: ステータスでフィルタ（オプション）
        sort: ソート順（デフォルト: -created_at）
        limit: 取得件数（1-100、デフォルト: 20）
        offset: オフセット（デフォルト: 0）

    Returns:
        PaginatedTravelPlanResponse: ページネーション情報付き旅行計画リスト
    """
    # フィルタ条件を構築
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if status:
        filters["status"] = status

    # ページネーション付きで取得
    total = repository.count(filters)
    plans = repository.find_with_pagination(
        filters=filters,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    return PaginatedTravelPlanResponse(
        items=[TravelPlanListResponse.from_dto(dto) for dto in plans],
        total=total,
        limit=limit,
        offset=offset,
    )
```

**レスポンススキーマ**:
```python
class PaginatedTravelPlanResponse(BaseModel):
    items: list[TravelPlanListResponse]
    total: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total
```

**レスポンス例**:
```json
{
  "items": [
    {
      "id": "plan_123",
      "title": "京都歴史探訪",
      "destination": "京都",
      "status": "planning",
      "guideGenerationStatus": "pending",
      "reflectionGenerationStatus": "pending"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

**改善ポイント**:
- ✅ ページネーション機能を追加（limit、offset）
- ✅ フィルタリング機能を追加（user_id、status）
- ✅ ソート機能を追加（sort）
- ✅ クエリパラメータのバリデーション（Query with ge/le）
- ✅ 総件数を返す（total）
- ✅ ページネーション情報をレスポンスに含める

## 例4: リレーションシップの表現

### Before（悪い設計）

```python
# パターン1: 過度なネスト
GET /api/v1/users/{user_id}/travel-plans/{plan_id}/guides/{guide_id}/sections/{section_id}

# パターン2: 完全にフラット（関連が不明確）
GET /api/v1/sections/{section_id}
```

**問題点（パターン1）**:
- 階層が深すぎる（4階層）
- URIが長くなりすぎる
- クライアントが複数のIDを管理する必要がある

**問題点（パターン2）**:
- リソース間の関連が不明確
- ドメインモデルが表現されていない

### After（良い設計）

```python
# 旅行計画に関連するガイド一覧
@router.get(
    "/{plan_id}/guides",
    response_model=list[TravelGuideResponse],
    summary="旅行計画のガイド一覧を取得",
)
def list_travel_guides(plan_id: str):
    """旅行計画に関連するガイド一覧を取得する"""
    ...

# 個別ガイド取得（サブリソースIDで直接アクセス）
@router.get(
    "/guides/{guide_id}",
    response_model=TravelGuideResponse,
    summary="ガイドを取得",
)
def get_travel_guide(guide_id: str):
    """ガイドを取得する"""
    ...

# または、親リソースのレスポンスに埋め込む
@router.get(
    "/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を取得",
)
def get_travel_plan(plan_id: str):
    """旅行計画を取得する（関連ガイドを含む）"""
    dto = use_case.execute(plan_id=plan_id)
    return TravelPlanResponse(**dto.__dict__)
```

**レスポンス例（埋め込み）**:
```json
{
  "id": "plan_123",
  "title": "京都歴史探訪",
  "destination": "京都",
  "status": "planning",
  "guide": {
    "id": "guide_456",
    "title": "京都の歴史ガイド",
    "content": "..."
  },
  "reflection": null
}
```

**改善ポイント**:
- ✅ 階層を2階層に制限
- ✅ サブリソースは親リソースのコンテキストで取得（`/{plan_id}/guides`）
- ✅ 個別サブリソースは独立して取得可能（`/guides/{guide_id}`）
- ✅ 関連リソースをレスポンスに埋め込む選択肢も提供
- ✅ N+1問題を回避（必要に応じてeager loading）

## 例5: バージョニング

### Before（悪い設計）

```python
# バージョニングなし
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "destination": "京都",
        "status": "planning",
    }

# 新しい要件: statusを詳細化したい
# 破壊的変更を直接実装
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "destination": "京都",
        # 破壊的変更: statusの構造を変更
        "status": {
            "value": "planning",
            "updatedAt": "2025-01-30T10:00:00Z"
        },
    }
```

**問題点**:
- バージョニングなし
- 既存クライアントが破損する
- 下位互換性がない

### After（良い設計）

```python
# v1: 既存のAPI
@router.get("/v1/travel-plans/{plan_id}")
def get_travel_plan_v1(plan_id: str):
    """旅行計画を取得する（v1）"""
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "destination": "京都",
        "status": "planning",
    }

# v2: 新しい要件に対応（非破壊的変更）
@router.get("/v2/travel-plans/{plan_id}")
def get_travel_plan_v2(plan_id: str):
    """旅行計画を取得する（v2）"""
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "destination": "京都",
        # 既存フィールドは維持（下位互換性）
        "status": "planning",
        # 新しいフィールドを追加
        "statusDetail": {
            "value": "planning",
            "updatedAt": "2025-01-30T10:00:00Z",
            "updatedBy": "user_123"
        },
        # その他の新しいフィールド
        "tags": ["歴史", "文化"],
    }
```

**または、非破壊的変更として同一バージョン内で実装**:

```python
# v1: フィールドを追加（既存フィールドは維持）
@router.get("/v1/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    """旅行計画を取得する"""
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "destination": "京都",
        # 既存フィールド（維持）
        "status": "planning",
        # 新しいフィールド（追加）
        "statusDetail": {
            "value": "planning",
            "updatedAt": "2025-01-30T10:00:00Z",
            "updatedBy": "user_123"
        } if include_detail else None,
    }
```

**改善ポイント**:
- ✅ URLバージョニングを使用（`/v1/`, `/v2/`）
- ✅ 既存のv1 APIは維持（下位互換性）
- ✅ 新しい機能はv2で提供
- ✅ 非破壊的変更（フィールド追加）は同一バージョン内で実装可能
- ✅ クライアントは段階的に移行可能

**バージョン移行計画**:
1. v2をリリース（v1は維持）
2. クライアントに移行を通知
3. 十分な移行期間を設ける（例: 6ヶ月）
4. v1を非推奨（deprecated）としてマーク
5. v1のサポート終了日を告知
6. v1を削除

## まとめ

API設計改善のポイント:

1. **CRUD API**: リソース指向設計、HTTPメソッドの正しい使用、適切なステータスコード
2. **エラーハンドリング**: 適切なステータスコード、構造化されたエラーレスポンス
3. **ページネーション**: limit/offset、フィルタリング、ソート、総件数の返却
4. **リレーションシップ**: 適切なネストレベル、サブリソースと埋め込みの使い分け
5. **バージョニング**: URLバージョニング、下位互換性の維持、段階的移行

これらの改善を適用することで、保守性が高く、使いやすいAPIを設計できる。
