# API設計のアンチパターン

## 概要

API設計において避けるべきアンチパターンを示す。これらのパターンは、保守性、拡張性、開発者体験を低下させる。

## 1. URIに動詞を含める

### アンチパターン

```
GET  /api/getTravelPlan?id=123
POST /api/createTravelPlan
POST /api/updateTravelPlan?id=123
POST /api/deleteTravelPlan?id=123
```

### 問題点

- HTTPメソッドのセマンティクスを無視している
- URIが冗長で読みにくい
- RESTful設計の原則に反する

### 正しい設計

```
GET    /api/v1/travel-plans/123
POST   /api/v1/travel-plans
PUT    /api/v1/travel-plans/123
DELETE /api/v1/travel-plans/123
```

## 2. 不適切なHTTPメソッド使用

### アンチパターン

```python
# GETで副作用のある操作を行う
@router.get("/travel-plans/delete/{plan_id}")
def delete_travel_plan(plan_id: str):
    repository.delete(plan_id)
    return {"message": "deleted"}

# すべての操作をPOSTで行う
@router.post("/travel-plans/get")
def get_travel_plan(request: GetTravelPlanRequest):
    ...
```

### 問題点

- GETは安全なメソッドだが、副作用がある
- ブラウザのプリフェッチやキャッシュで意図しない削除が発生する可能性
- HTTPメソッドのセマンティクスを無視している

### 正しい設計

```python
@router.delete("/travel-plans/{plan_id}")
def delete_travel_plan(plan_id: str):
    repository.delete(plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    ...
```

## 3. ステータスコードの誤用

### アンチパターン

```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    plan = repository.find(plan_id)
    if not plan:
        # 常に200を返す
        return {"error": "Travel plan not found"}
    return plan
```

### 問題点

- エラー時も200 OKを返している
- クライアントがエラーを検出しにくい
- HTTPステータスコードの意味を無視している

### 正しい設計

```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    plan = repository.find(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        )
    return plan
```

## 4. 過度なネスト

### アンチパターン

```
GET /api/v1/users/{user_id}/travel-plans/{plan_id}/guides/{guide_id}/sections/{section_id}/items/{item_id}
```

### 問題点

- URIが長すぎて読みにくい
- 階層が深すぎる（5階層）
- クライアントが複数のIDを管理する必要がある

### 正しい設計

```
# 階層を2階層までに制限
GET /api/v1/travel-plans/{plan_id}/guides
GET /api/v1/guides/{guide_id}/sections
GET /api/v1/sections/{section_id}/items

# または、個別リソースに直接アクセス
GET /api/v1/items/{item_id}
```

## 5. 一貫性のない命名

### アンチパターン

```
/api/v1/travel-plans    # ケバブケース
/api/v1/travel_guides   # スネークケース
/api/v1/travelPlans     # キャメルケース（URIには使用しない）
```

### 問題点

- 一貫性がなく、混乱を招く
- 開発者が覚えにくい

### 正しい設計

```
/api/v1/travel-plans
/api/v1/travel-guides
/api/v1/reflections
```

**すべてケバブケースで統一。**

## 6. エラーメッセージの不足

### アンチパターン

```python
@router.post("/travel-plans")
def create_travel_plan(request: CreateTravelPlanRequest):
    try:
        ...
    except Exception:
        # エラーの詳細を返さない
        raise HTTPException(status_code=500, detail="Error")
```

**レスポンス例**:
```json
{
  "detail": "Error"
}
```

### 問題点

- エラーの原因がわからない
- デバッグが困難
- クライアントが適切なエラーハンドリングを実装できない

### 正しい設計

```python
@router.post("/travel-plans")
def create_travel_plan(request: CreateTravelPlanRequest):
    try:
        ...
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "fields": {"title": "must not be empty"},
            },
        )
```

**レスポンス例**:
```json
{
  "detail": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "fields": {
      "title": "must not be empty"
    }
  }
}
```

## 7. バージョニングの欠如

### アンチパターン

```
/api/travel-plans    # バージョンなし
```

**後で仕様を変更**:
```python
# 破壊的変更を直接実装
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    return {
        "id": plan_id,
        # statusの構造を変更（破壊的変更）
        "status": {
            "value": "planning",
            "updatedAt": "2025-01-30T10:00:00Z"
        },
    }
```

### 問題点

- 既存クライアントが破損する
- 下位互換性がない
- バージョン管理ができない

### 正しい設計

```
/api/v1/travel-plans    # v1
/api/v2/travel-plans    # v2（破壊的変更時）
```

**v1は維持し、v2で新しい仕様を提供。**

## 8. セキュリティ考慮の欠如

### アンチパターン

```python
# 認証なし
@router.delete("/travel-plans/{plan_id}")
def delete_travel_plan(plan_id: str):
    repository.delete(plan_id)
    return {"message": "deleted"}

# SQLインジェクションの脆弱性
@router.get("/travel-plans")
def list_travel_plans(user_id: str):
    query = f"SELECT * FROM travel_plans WHERE user_id = '{user_id}'"
    ...
```

### 問題点

- 認証・認可がない
- SQLインジェクションの脆弱性
- 誰でもデータを削除できる

### 正しい設計

```python
# 認証・認可を実装
@router.delete("/travel-plans/{plan_id}")
def delete_travel_plan(
    plan_id: str,
    user: dict = Depends(verify_token),
):
    # 権限チェック
    plan = repository.find(plan_id)
    if plan.user_id != user["sub"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    repository.delete(plan_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ORMを使用（SQLインジェクション対策）
@router.get("/travel-plans")
def list_travel_plans(
    user_id: str,
    user: dict = Depends(verify_token),
):
    plans = repository.find_by_user_id(user_id)
    ...
```

## 9. ページネーションの欠如

### アンチパターン

```python
@router.get("/travel-plans")
def list_travel_plans():
    # すべてのデータを一度に返す
    plans = repository.find_all()
    return plans
```

### 問題点

- データ量が増えるとパフォーマンスが低下
- レスポンスサイズが巨大化
- メモリ不足の原因となる

### 正しい設計

```python
@router.get("/travel-plans")
def list_travel_plans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    total = repository.count()
    plans = repository.find_with_pagination(limit=limit, offset=offset)
    return {
        "items": plans,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
```

## 10. 暗黙的なフォールバック

### アンチパターン

```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    plan = repository.find(plan_id)
    # リソースが見つからない場合、デフォルト値を返す
    if not plan:
        return {
            "id": "unknown",
            "title": "Unknown",
            "destination": "Unknown",
        }
    return plan
```

### 問題点

- リソースが存在しないのに200 OKを返す
- クライアントがエラーを検出できない
- 暗黙的な動作で混乱を招く

### 正しい設計

```python
@router.get("/travel-plans/{plan_id}")
def get_travel_plan(plan_id: str):
    plan = repository.find(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        )
    return plan
```

## 11. レスポンスボディの不一致

### アンチパターン

```python
# 成功時
@router.post("/travel-plans")
def create_travel_plan(request: CreateTravelPlanRequest):
    plan = repository.create(request)
    return {"data": plan, "status": "success"}

# エラー時
@router.post("/travel-plans")
def create_travel_plan(request: CreateTravelPlanRequest):
    try:
        ...
    except ValueError as e:
        return {"error": str(e), "code": 400}
```

### 問題点

- 成功時とエラー時でレスポンス構造が異なる
- クライアントが処理しにくい

### 正しい設計

```python
# 成功時はリソースをそのまま返す
@router.post("/travel-plans", status_code=status.HTTP_201_CREATED)
def create_travel_plan(request: CreateTravelPlanRequest):
    plan = repository.create(request)
    return plan

# エラー時はHTTPExceptionを使用
@router.post("/travel-plans")
def create_travel_plan(request: CreateTravelPlanRequest):
    try:
        ...
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
```

## 12. 過度な抽象化

### アンチパターン

```
# すべての操作を単一のエンドポイントで処理
POST /api/v1/execute
{
  "action": "get_travel_plan",
  "params": {"plan_id": "123"}
}
```

### 問題点

- RESTfulの原則に反する
- HTTPメソッドのセマンティクスを無視
- キャッシュが効かない
- ドキュメント化が困難

### 正しい設計

```
GET    /api/v1/travel-plans/123
POST   /api/v1/travel-plans
PUT    /api/v1/travel-plans/123
DELETE /api/v1/travel-plans/123
```

## まとめ

避けるべきアンチパターン:

1. **URIに動詞を含める**: リソース名を名詞にし、HTTPメソッドで操作を表現
2. **不適切なHTTPメソッド**: GET/POST/PUT/DELETE を正しく使用
3. **ステータスコードの誤用**: 適切なステータスコードを返す
4. **過度なネスト**: 階層を2階層までに制限
5. **一貫性のない命名**: ケバブケースで統一
6. **エラーメッセージの不足**: 詳細なエラー情報を提供
7. **バージョニングの欠如**: URLバージョニングを使用
8. **セキュリティ考慮の欠如**: 認証・認可、入力バリデーションを実装
9. **ページネーションの欠如**: limit/offsetでページネーション
10. **暗黙的なフォールバック**: エラーは明示的に返す
11. **レスポンスボディの不一致**: 一貫したレスポンス構造
12. **過度な抽象化**: RESTful設計の原則に従う

これらのアンチパターンを避けることで、保守性が高く、使いやすいAPIを設計できる。
