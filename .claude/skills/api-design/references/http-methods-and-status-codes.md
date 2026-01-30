# HTTPメソッドとステータスコード

## 概要

HTTPメソッドとステータスコードは、RESTful APIの中核をなす要素である。適切なメソッドとステータスコードの使用は、APIの意図を明確にし、開発者体験を向上させる。

## HTTPメソッド詳細

### GET - リソース取得

**用途**: リソースまたはリソースのコレクションを取得する。

**特性**:
- **冪等性**: ✅（何度実行しても同じ結果）
- **安全性**: ✅（リソースを変更しない）
- **リクエストボディ**: なし
- **レスポンスボディ**: あり

**使用例**:
```python
# 個別リソース取得
@router.get("/{plan_id}", response_model=TravelPlanResponse)
def get_travel_plan(plan_id: str):
    ...
    return TravelPlanResponse(**dto.__dict__)

# コレクション取得
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(user_id: str):
    ...
    return [TravelPlanListResponse.from_dto(dto) for dto in dtos]
```

**成功時のステータスコード**:
- `200 OK`: リソースが正常に取得された

**エラー時のステータスコード**:
- `404 Not Found`: リソースが存在しない
- `400 Bad Request`: パラメータが不正

**注意点**:
- GETリクエストでリソースを変更してはならない（Safe）
- 大量のフィルタ条件が必要な場合は、POSTで検索エンドポイントを作成する場合もある

### POST - リソース作成

**用途**: 新しいリソースを作成する。

**特性**:
- **冪等性**: ❌（複数回実行すると複数のリソースが作成される）
- **安全性**: ❌（リソースを変更する）
- **リクエストボディ**: あり
- **レスポンスボディ**: あり（作成されたリソース）

**使用例**:
```python
@router.post(
    "",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_travel_plan(request: CreateTravelPlanRequest):
    use_case = CreateTravelPlanUseCase(repository)
    dto = use_case.execute(
        user_id=request.user_id,
        title=request.title,
        destination=request.destination,
        spots=spots_dict,
    )
    return TravelPlanResponse(**dto.__dict__)
```

**成功時のステータスコード**:
- `201 Created`: リソースが正常に作成された
- `200 OK`: リソースは作成されたが、201を返さない実装（非推奨）

**エラー時のステータスコード**:
- `400 Bad Request`: バリデーションエラー
- `409 Conflict`: リソースの競合（例: 既に同じIDのリソースが存在する）

**ベストプラクティス**:
- 作成されたリソースのURIを`Location`ヘッダーに含める
- 作成されたリソース全体をレスポンスボディに含める

**プロジェクト実装例**:
```python
# backend/app/interfaces/api/v1/travel_plans.py:66-105
@router.post(
    "",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="旅行計画を作成",
)
def create_travel_plan(
    request: CreateTravelPlanRequest,
    repository: TravelPlanRepository = Depends(get_repository),
) -> TravelPlanResponse:
    use_case = CreateTravelPlanUseCase(repository)
    spots_dict = [spot.model_dump(by_alias=True) for spot in request.spots]
    try:
        dto = use_case.execute(
            user_id=request.user_id,
            title=request.title,
            destination=request.destination,
            spots=spots_dict,
        )
        return TravelPlanResponse(**dto.__dict__)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
```

### PUT - リソース全体更新

**用途**: 既存リソース全体を更新する（完全置換）。

**特性**:
- **冪等性**: ✅（何度実行しても同じ結果）
- **安全性**: ❌（リソースを変更する）
- **リクエストボディ**: あり（リソース全体）
- **レスポンスボディ**: あり（更新後のリソース）

**使用例**:
```python
@router.put("/{plan_id}", response_model=TravelPlanResponse)
def update_travel_plan(
    plan_id: str,
    request: UpdateTravelPlanRequest,
):
    # リソース全体を更新
    dto = use_case.execute(
        plan_id=plan_id,
        title=request.title,
        destination=request.destination,
        spots=spots_dict,
        status=request.status,
    )
    return TravelPlanResponse(**dto.__dict__)
```

**成功時のステータスコード**:
- `200 OK`: リソースが正常に更新された
- `204 No Content`: リソースは更新されたが、レスポンスボディを返さない

**エラー時のステータスコード**:
- `404 Not Found`: リソースが存在しない
- `400 Bad Request`: バリデーションエラー
- `409 Conflict`: リソースの競合

**注意点**:
- PUTはリソース全体を置き換えるため、すべてのフィールドを送信する必要がある
- 一部のフィールドのみを更新する場合はPATCHを使用する

**PUTの冪等性**:
同じリクエストを複数回送信しても、結果は同じになる。

```python
# 1回目のPUT
PUT /api/v1/travel-plans/plan_123
{
  "title": "京都歴史探訪",
  "destination": "京都",
  "status": "planning"
}

# 2回目のPUT（同じリクエスト）
PUT /api/v1/travel-plans/plan_123
{
  "title": "京都歴史探訪",
  "destination": "京都",
  "status": "planning"
}

# 結果は同じ（冪等）
```

### PATCH - リソース部分更新

**用途**: 既存リソースの一部のフィールドのみを更新する。

**特性**:
- **冪等性**: △（実装による）
- **安全性**: ❌（リソースを変更する）
- **リクエストボディ**: あり（更新するフィールドのみ）
- **レスポンスボディ**: あり（更新後のリソース）

**使用例**:
```python
# ステータスのみを更新
PATCH /api/v1/travel-plans/plan_123
{
  "status": "ongoing"
}

# タイトルと目的地を更新
PATCH /api/v1/travel-plans/plan_123
{
  "title": "京都・奈良歴史探訪",
  "destination": "京都・奈良"
}
```

**成功時のステータスコード**:
- `200 OK`: リソースが正常に更新された

**エラー時のステータスコード**:
- `404 Not Found`: リソースが存在しない
- `400 Bad Request`: バリデーションエラー

**PUTとPATCHの使い分け**:

| 操作 | メソッド | リクエストボディ |
|------|---------|----------------|
| リソース全体を置換 | PUT | すべてのフィールド |
| 一部のフィールドのみ更新 | PATCH | 更新するフィールドのみ |

**プロジェクト実装例**:

プロジェクトではPUTを使用しているが、リクエストスキーマで一部フィールドをオプションにすることでPATCHのような動作を実現している。

```python
# backend/app/interfaces/schemas/travel_plan.py:46-74
class UpdateTravelPlanRequest(BaseModel):
    title: str | None = Field(None, min_length=1, description="旅行タイトル")
    destination: str | None = Field(None, min_length=1, description="目的地")
    spots: list[TouristSpotSchema] | None = Field(None, description="観光スポットリスト")
    status: str | None = Field(None, description="旅行状態")
```

### DELETE - リソース削除

**用途**: 既存リソースを削除する。

**特性**:
- **冪等性**: ✅（何度実行しても結果は同じ）
- **安全性**: ❌（リソースを変更する）
- **リクエストボディ**: なし
- **レスポンスボディ**: なし（204の場合）または削除結果

**使用例**:
```python
@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_travel_plan(plan_id: str):
    use_case = DeleteTravelPlanUseCase(repository)
    use_case.execute(plan_id=plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

**成功時のステータスコード**:
- `204 No Content`: リソースが正常に削除された（レスポンスボディなし）
- `200 OK`: リソースは削除され、削除結果を返す

**エラー時のステータスコード**:
- `404 Not Found`: リソースが存在しない

**DELETEの冪等性**:

```python
# 1回目のDELETE
DELETE /api/v1/travel-plans/plan_123
# 結果: 204 No Content（削除成功）

# 2回目のDELETE（同じリソース）
DELETE /api/v1/travel-plans/plan_123
# 結果: 404 Not Found（リソースは既に削除済み）

# 冪等性: 2回目以降も状態は同じ（リソースは存在しない）
```

**プロジェクト実装例**:
```python
# backend/app/interfaces/api/v1/travel_plans.py:232-263
@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="旅行計画を削除",
)
def delete_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
) -> Response:
    use_case = DeleteTravelPlanUseCase(repository)
    try:
        use_case.execute(plan_id=plan_id)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

## HTTPステータスコード詳細

### 成功系（2xx）

#### 200 OK

**用途**: リクエストが成功した。

**使用場面**:
- GET: リソース取得成功
- PUT: リソース更新成功
- PATCH: リソース部分更新成功
- POST: リソース作成成功（201を使わない場合）

**レスポンスボディ**: あり

#### 201 Created

**用途**: 新しいリソースが作成された。

**使用場面**:
- POST: リソース作成成功

**レスポンスボディ**: あり（作成されたリソース）

**推奨ヘッダー**:
```
Location: /api/v1/travel-plans/plan_123
```

#### 204 No Content

**用途**: リクエストは成功したが、返すコンテンツがない。

**使用場面**:
- DELETE: リソース削除成功
- PUT/PATCH: リソース更新成功（レスポンスボディを返さない場合）

**レスポンスボディ**: なし

### クライアントエラー（4xx）

#### 400 Bad Request

**用途**: クライアントのリクエストが不正。

**使用場面**:
- バリデーションエラー
- 必須パラメータの欠落
- 不正なフォーマット

**エラーレスポンス例**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "must not be empty",
      "destination": "must not be empty"
    }
  }
}
```

**プロジェクト実装例**:
```python
# backend/app/interfaces/api/v1/travel_plans.py:101-105
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e),
    ) from e
```

#### 401 Unauthorized

**用途**: 認証が必要、または認証に失敗。

**使用場面**:
- 認証トークンがない
- 認証トークンが無効
- 認証トークンの有効期限切れ

**エラーレスポンス例**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

**推奨ヘッダー**:
```
WWW-Authenticate: Bearer
```

#### 403 Forbidden

**用途**: 認証は成功したが、リソースへのアクセス権限がない。

**使用場面**:
- ユーザーが他のユーザーのリソースにアクセスしようとした
- 権限が不足している

**エラーレスポンス例**:
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You do not have permission to access this resource"
  }
}
```

**401と403の使い分け**:
- `401 Unauthorized`: 認証していない（ログインしていない）
- `403 Forbidden`: 認証しているが、権限がない

#### 404 Not Found

**用途**: 指定されたリソースが見つからない。

**使用場面**:
- 存在しないリソースIDを指定
- 削除済みのリソースにアクセス

**エラーレスポンス例**:
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

**プロジェクト実装例**:
```python
# backend/app/interfaces/api/v1/travel_plans.py:174-178
except TravelPlanNotFoundError as e:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Travel plan not found: {plan_id}",
    ) from e
```

#### 409 Conflict

**用途**: リクエストがリソースの現在の状態と競合している。

**使用場面**:
- 既に存在するリソースを作成しようとした
- 楽観的ロックの競合
- ビジネスルールの違反

**エラーレスポンス例**:
```json
{
  "error": {
    "code": "RESOURCE_CONFLICT",
    "message": "Travel plan with the same title already exists",
    "details": {
      "existing_plan_id": "plan_456"
    }
  }
}
```

### サーバーエラー（5xx）

#### 500 Internal Server Error

**用途**: サーバー内部でエラーが発生した。

**使用場面**:
- 予期しない例外
- データベース接続エラー
- 外部APIエラー

**エラーレスポンス例**:
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

**注意**: エラーの詳細情報（スタックトレースなど）をクライアントに返さない。

#### 503 Service Unavailable

**用途**: サービスが一時的に利用できない。

**使用場面**:
- メンテナンス中
- サーバー過負荷
- 依存サービスがダウン

**推奨ヘッダー**:
```
Retry-After: 3600
```

## エラーレスポンスボディの設計

### 推奨構造

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field1": "error detail",
      "field2": "error detail"
    }
  }
}
```

### フィールド説明

- **code**: 機械的に処理可能なエラーコード（大文字スネークケース）
- **message**: 人間が読める形式のエラーメッセージ
- **details**: エラーの詳細情報（オプション）

### RFC 7807（Problem Details）

標準化されたエラーレスポンス形式。

```json
{
  "type": "https://example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "The request body contains invalid fields",
  "instance": "/api/v1/travel-plans",
  "errors": {
    "title": "must not be empty",
    "destination": "must not be empty"
  }
}
```

**Content-Type**: `application/problem+json`

## Before/After実例

### 例1: ステータスコードの改善

**Before**（悪い設計）:
```python
@router.post("/travel-plans")
def create_travel_plan(request: CreateTravelPlanRequest):
    # 常に200を返す
    return {"message": "created", "data": plan}
```

**After**（良い設計）:
```python
@router.post("/travel-plans", status_code=status.HTTP_201_CREATED)
def create_travel_plan(request: CreateTravelPlanRequest):
    # 201 Createdを返す
    return TravelPlanResponse(**dto.__dict__)
```

### 例2: エラーハンドリングの改善

**Before**（悪い設計）:
```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    plan = repository.find(plan_id)
    if not plan:
        # 常に200を返し、エラーメッセージを含める
        return {"error": "Travel plan not found"}
    return plan
```

**After**（良い設計）:
```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except TravelPlanNotFoundError as e:
        # 404を返す
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
```

### 例3: DELETEの改善

**Before**（悪い設計）:
```python
@router.delete("/travel-plans/{plan_id}")
def delete_travel_plan(plan_id: str):
    repository.delete(plan_id)
    # 200 OKとメッセージを返す
    return {"message": "deleted"}
```

**After**（良い設計）:
```python
@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_travel_plan(plan_id: str):
    try:
        use_case.execute(plan_id=plan_id)
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
    # 204 No Contentを返す
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

## まとめ

HTTPメソッドとステータスコードのポイント:

1. **HTTPメソッドのセマンティクスを理解**: GET（取得）、POST（作成）、PUT（全体更新）、PATCH（部分更新）、DELETE（削除）
2. **冪等性を考慮**: GET、PUT、DELETEは冪等、POSTは非冪等
3. **適切なステータスコードを使用**: 成功（200/201/204）、クライアントエラー（400/401/403/404/409）、サーバーエラー（500/503）
4. **エラーレスポンスを構造化**: エラーコード、メッセージ、詳細情報を含める
5. **一貫性を保つ**: プロジェクト全体で同じパターンを使用

これらの原則を守ることで、明確で使いやすいAPIを設計できる。
