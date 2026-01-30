# ページネーション、フィルタリング、ソート

## 概要

大量のデータを扱うAPIでは、ページネーション、フィルタリング、ソートの機能が不可欠である。これらの機能により、クライアントは必要なデータのみを効率的に取得でき、パフォーマンスとユーザー体験が向上する。

## ページネーション

### オフセットベースページネーション

**概要**: `offset`と`limit`パラメータを使用してデータの範囲を指定する。

**パラメータ**:
- `limit`: 取得件数（デフォルト: 20、最大: 100など）
- `offset`: 開始位置（デフォルト: 0）

**例**:
```
GET /api/v1/travel-plans?limit=20&offset=0   # 1ページ目（0-19件目）
GET /api/v1/travel-plans?limit=20&offset=20  # 2ページ目（20-39件目）
GET /api/v1/travel-plans?limit=20&offset=40  # 3ページ目（40-59件目）
```

**実装例**:
```python
@router.get("", response_model=PaginatedTravelPlanResponse)
def list_travel_plans(
    limit: int = Query(20, ge=1, le=100, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
):
    """旅行計画一覧を取得する（ページネーション付き）"""
    total = repository.count()
    plans = repository.find_with_pagination(limit=limit, offset=offset)

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
        """次のページが存在するか"""
        return self.offset + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """前のページが存在するか"""
        return self.offset > 0
```

**レスポンス例**:
```json
{
  "items": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

**メリット**:
- シンプルで理解しやすい
- 特定のページに直接ジャンプできる
- 総件数を取得しやすい

**デメリット**:
- データが追加/削除されるとページがずれる
- 大きなoffsetではパフォーマンスが低下する（データベースがすべてスキップする行を読む必要がある）

### ページ番号ベースページネーション

**概要**: `page`と`page_size`パラメータを使用する。

**パラメータ**:
- `page`: ページ番号（1から始まる）
- `page_size`: 1ページあたりの件数

**例**:
```
GET /api/v1/travel-plans?page=1&page_size=20  # 1ページ目
GET /api/v1/travel-plans?page=2&page_size=20  # 2ページ目
GET /api/v1/travel-plans?page=3&page_size=20  # 3ページ目
```

**実装例**:
```python
@router.get("", response_model=PaginatedTravelPlanResponse)
def list_travel_plans(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="ページサイズ"),
):
    """旅行計画一覧を取得する（ページ番号ベース）"""
    offset = (page - 1) * page_size
    total = repository.count()
    plans = repository.find_with_pagination(limit=page_size, offset=offset)

    return PaginatedTravelPlanResponse(
        items=[TravelPlanListResponse.from_dto(dto) for dto in plans],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )
```

**レスポンス例**:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

**メリット**:
- ユーザーにとって直感的（「3ページ目」など）
- UIでページ番号を表示しやすい

**デメリット**:
- オフセットベースと同じパフォーマンス問題

### カーソルベースページネーション

**概要**: カーソル（次のページを取得するためのポインタ）を使用する。

**パラメータ**:
- `cursor`: 次のページのカーソル（前回のレスポンスから取得）
- `limit`: 取得件数

**例**:
```
GET /api/v1/travel-plans?limit=20                         # 1ページ目
GET /api/v1/travel-plans?cursor=eyJpZCI6MTIzfQ&limit=20  # 2ページ目
```

**実装例**:
```python
import base64
import json

@router.get("", response_model=CursorPaginatedResponse)
def list_travel_plans(
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    """旅行計画一覧を取得する（カーソルベース）"""
    # カーソルをデコード
    after_id = None
    if cursor:
        decoded = base64.b64decode(cursor).decode()
        after_id = json.loads(decoded)["id"]

    # カーソル以降のデータを取得
    plans = repository.find_after_cursor(after_id=after_id, limit=limit + 1)

    # 次のページが存在するかチェック
    has_next = len(plans) > limit
    if has_next:
        plans = plans[:limit]

    # 次のカーソルを生成
    next_cursor = None
    if has_next and plans:
        last_id = plans[-1].id
        cursor_data = json.dumps({"id": last_id})
        next_cursor = base64.b64encode(cursor_data.encode()).decode()

    return CursorPaginatedResponse(
        items=[TravelPlanListResponse.from_dto(dto) for dto in plans],
        next_cursor=next_cursor,
        has_next=has_next,
    )
```

**レスポンススキーマ**:
```python
class CursorPaginatedResponse(BaseModel):
    items: list[TravelPlanListResponse]
    next_cursor: str | None
    has_next: bool
```

**レスポンス例**:
```json
{
  "items": [...],
  "next_cursor": "eyJpZCI6MTIzfQ==",
  "has_next": true
}
```

**メリット**:
- データが追加/削除されてもページがずれない
- 大量のデータでもパフォーマンスが一定
- リアルタイムフィードに最適

**デメリット**:
- 特定のページに直接ジャンプできない
- 総件数を取得しにくい
- 実装が複雑

### ページネーション方式の選択

| 用途 | 推奨方式 | 理由 |
|------|---------|------|
| 管理画面、検索結果 | オフセットまたはページ番号 | ページジャンプ、総件数表示が必要 |
| リアルタイムフィード | カーソル | データの追加/削除に強い |
| モバイルアプリ | カーソル | 無限スクロールに最適 |
| データエクスポート | オフセット | 実装がシンプル |

## フィルタリング

### 基本的なフィルタリング

リソースのフィールド名をそのままクエリパラメータ名に使用する。

**例**:
```
GET /api/v1/travel-plans?user_id=user_123
GET /api/v1/travel-plans?status=planning
GET /api/v1/travel-plans?user_id=user_123&status=planning
```

**実装例**:
```python
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    user_id: str | None = Query(None, description="ユーザーIDでフィルタ"),
    status: str | None = Query(None, description="ステータスでフィルタ"),
):
    """旅行計画一覧を取得する（フィルタ付き）"""
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if status:
        filters["status"] = status

    plans = repository.find_by_filters(filters)
    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

**プロジェクト実装例**:
```python
# backend/app/interfaces/api/v1/travel_plans.py:113-135
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    user_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
):
    use_case = ListTravelPlansUseCase(repository)
    dtos = use_case.execute(user_id=user_id)
    return [TravelPlanListResponse.from_dto(dto) for dto in dtos]
```

### 複数値フィルタリング

同じパラメータ名を複数回指定する。

**例**:
```
GET /api/v1/travel-plans?status=planning&status=ongoing
```

**実装例**:
```python
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    status: list[str] = Query([], description="ステータスでフィルタ（複数可）"),
):
    """旅行計画一覧を取得する（複数ステータスフィルタ）"""
    filters = {}
    if status:
        filters["status__in"] = status

    plans = repository.find_by_filters(filters)
    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

### 範囲フィルタリング

日付や数値の範囲でフィルタリングする。

**パターン1: 接尾辞を使用**:
```
GET /api/v1/travel-plans?created_at_gte=2025-01-01&created_at_lte=2025-01-31
```

**パターン2: 範囲パラメータ**:
```
GET /api/v1/travel-plans?created_at_range=2025-01-01,2025-01-31
```

**実装例（パターン1）**:
```python
from datetime import datetime

@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    created_at_gte: datetime | None = Query(None, description="作成日時（以上）"),
    created_at_lte: datetime | None = Query(None, description="作成日時（以下）"),
):
    """旅行計画一覧を取得する（日付範囲フィルタ）"""
    filters = {}
    if created_at_gte:
        filters["created_at__gte"] = created_at_gte
    if created_at_lte:
        filters["created_at__lte"] = created_at_lte

    plans = repository.find_by_filters(filters)
    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

### 部分一致検索

テキストフィールドの部分一致検索。

**例**:
```
GET /api/v1/travel-plans?title_contains=京都
GET /api/v1/travel-plans?destination_startswith=東京
```

**実装例**:
```python
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    title_contains: str | None = Query(None, description="タイトルに含まれる文字列"),
    destination_startswith: str | None = Query(None, description="目的地の先頭文字列"),
):
    """旅行計画一覧を取得する（テキスト検索）"""
    filters = {}
    if title_contains:
        filters["title__contains"] = title_contains
    if destination_startswith:
        filters["destination__startswith"] = destination_startswith

    plans = repository.find_by_filters(filters)
    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

## ソート

### 基本的なソート

`sort`パラメータを使用し、降順はマイナス記号（`-`）をプレフィックスに付ける。

**例**:
```
GET /api/v1/travel-plans?sort=created_at      # 昇順（古い順）
GET /api/v1/travel-plans?sort=-created_at     # 降順（新しい順）
```

**実装例**:
```python
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    sort: str = Query("-created_at", description="ソート順"),
):
    """旅行計画一覧を取得する（ソート付き）"""
    # ソートフィールドと順序を解析
    if sort.startswith("-"):
        field = sort[1:]
        order = "desc"
    else:
        field = sort
        order = "asc"

    plans = repository.find_with_sort(field=field, order=order)
    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

### 複数フィールドのソート

カンマ区切りで複数のソートフィールドを指定する。

**例**:
```
GET /api/v1/travel-plans?sort=status,-created_at
# ステータス昇順 → 作成日時降順
```

**実装例**:
```python
@router.get("", response_model=list[TravelPlanListResponse])
def list_travel_plans(
    sort: str = Query("-created_at", description="ソート順（カンマ区切りで複数指定可）"),
):
    """旅行計画一覧を取得する（複数フィールドソート）"""
    # ソートフィールドのリストを解析
    sort_fields = []
    for s in sort.split(","):
        if s.startswith("-"):
            sort_fields.append({"field": s[1:], "order": "desc"})
        else:
            sort_fields.append({"field": s, "order": "asc"})

    plans = repository.find_with_multi_sort(sort_fields)
    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

## フィールド選択（Sparse Fieldsets）

クライアントが必要なフィールドのみを取得できるようにする。

**例**:
```
GET /api/v1/travel-plans?fields=id,title,status
```

**実装例**:
```python
@router.get("", response_model=list[dict])
def list_travel_plans(
    fields: str | None = Query(None, description="取得するフィールド（カンマ区切り）"),
):
    """旅行計画一覧を取得する（フィールド選択付き）"""
    plans = repository.find_all()

    # フィールド選択
    if fields:
        selected_fields = fields.split(",")
        return [
            {k: v for k, v in dto.__dict__.items() if k in selected_fields}
            for dto in plans
        ]

    return [TravelPlanListResponse.from_dto(dto) for dto in plans]
```

**レスポンス例**:
```json
[
  {
    "id": "plan_123",
    "title": "京都歴史探訪",
    "status": "planning"
  }
]
```

## 統合例

ページネーション、フィルタリング、ソートを組み合わせた実装例。

```python
@router.get("", response_model=PaginatedTravelPlanResponse)
def list_travel_plans(
    # フィルタリング
    user_id: str | None = Query(None, description="ユーザーIDでフィルタ"),
    status: list[str] = Query([], description="ステータスでフィルタ（複数可）"),
    created_at_gte: datetime | None = Query(None, description="作成日時（以上）"),
    created_at_lte: datetime | None = Query(None, description="作成日時（以下）"),
    # ソート
    sort: str = Query("-created_at", description="ソート順"),
    # ページネーション
    limit: int = Query(20, ge=1, le=100, description="取得件数"),
    offset: int = Query(0, ge=0, description="オフセット"),
):
    """旅行計画一覧を取得する（フル機能）

    Args:
        user_id: ユーザーIDでフィルタ
        status: ステータスでフィルタ（複数可）
        created_at_gte: 作成日時（以上）
        created_at_lte: 作成日時（以下）
        sort: ソート順
        limit: 取得件数
        offset: オフセット

    Returns:
        PaginatedTravelPlanResponse: ページネーション情報付き旅行計画リスト
    """
    # フィルタ条件を構築
    filters = {}
    if user_id:
        filters["user_id"] = user_id
    if status:
        filters["status__in"] = status
    if created_at_gte:
        filters["created_at__gte"] = created_at_gte
    if created_at_lte:
        filters["created_at__lte"] = created_at_lte

    # ソート条件を解析
    if sort.startswith("-"):
        sort_field = sort[1:]
        sort_order = "desc"
    else:
        sort_field = sort
        sort_order = "asc"

    # データ取得
    total = repository.count(filters)
    plans = repository.find_with_pagination_and_sort(
        filters=filters,
        sort_field=sort_field,
        sort_order=sort_order,
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

**リクエスト例**:
```
GET /api/v1/travel-plans?user_id=user_123&status=planning&status=ongoing&sort=-created_at&limit=10&offset=0
```

## まとめ

ページネーション、フィルタリング、ソートのポイント:

1. **ページネーション**: 用途に応じてオフセットベース、ページ番号ベース、カーソルベースを選択
2. **フィルタリング**: リソースのフィールド名をそのままパラメータ名に使用
3. **ソート**: `sort`パラメータを使用し、降順は`-`プレフィックス
4. **組み合わせ**: すべての機能を組み合わせて柔軟なAPI設計を実現
5. **バリデーション**: Queryパラメータでge/leを使用して値の範囲を制限

これらの機能を適切に実装することで、大量のデータを扱うAPIでも優れたパフォーマンスとユーザー体験を提供できる。
