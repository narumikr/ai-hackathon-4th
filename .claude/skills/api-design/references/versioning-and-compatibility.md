# バージョニングと互換性

## 概要

API仕様は進化する。新機能の追加、既存機能の改善、バグ修正などにより、APIは常に変化する。バージョニング戦略は、既存クライアントを破損させることなく、APIを進化させるための重要な設計要素である。

## バージョニング手法

### URLバージョニング（推奨）

**概要**: URLパスにバージョン番号を含める。

**例**:
```
/api/v1/travel-plans
/api/v2/travel-plans
```

**実装例**:
```python
# v1
v1_router = APIRouter(prefix="/v1")
v1_router.include_router(travel_plans_v1.router)

# v2
v2_router = APIRouter(prefix="/v2")
v2_router.include_router(travel_plans_v2.router)

# メインアプリに登録
app.include_router(v1_router, prefix="/api")
app.include_router(v2_router, prefix="/api")
```

**メリット**:
- **明示的でわかりやすい**: URLを見るだけでバージョンがわかる
- **ブラウザで直接アクセス可能**: デバッグが容易
- **ドキュメント化が容易**: バージョンごとにドキュメントを分けやすい
- **キャッシュと相性が良い**: URLが異なるため、バージョン間でキャッシュが混在しない

**デメリット**:
- URLが変わる（ただし、これは意図的な設計）

**プロジェクト実装例**:
```python
# backend/main.py:58-61
app.include_router(travel_plans.router, prefix="/api/v1")
app.include_router(travel_guides.router, prefix="/api/v1")
app.include_router(reflections.router, prefix="/api/v1")
app.include_router(uploads.router, prefix="/api/v1")
```

### ヘッダーバージョニング

**概要**: カスタムHTTPヘッダーでバージョンを指定する。

**例**:
```
GET /api/travel-plans
API-Version: 2
```

**実装例**:
```python
@router.get("/travel-plans")
def list_travel_plans(
    api_version: str = Header("1", alias="API-Version"),
):
    if api_version == "2":
        # v2の処理
        ...
    else:
        # v1の処理
        ...
```

**メリット**:
- URLが変わらない
- RESTfulの原則に忠実（リソースの識別子は変わらない）

**デメリット**:
- ブラウザで直接アクセスしにくい
- ドキュメント化が複雑
- デバッグが難しい

### メディアタイプバージョニング

**概要**: `Accept`ヘッダーでバージョンを指定する。

**例**:
```
GET /api/travel-plans
Accept: application/vnd.myapp.v2+json
```

**実装例**:
```python
@router.get("/travel-plans")
def list_travel_plans(
    accept: str = Header("application/json"),
):
    if "v2+json" in accept:
        # v2の処理
        ...
    else:
        # v1の処理
        ...
```

**メリット**:
- RESTfulの原則に最も忠実
- コンテンツネゴシエーションの標準に従う

**デメリット**:
- 実装が複雑
- デバッグが難しい
- 一般的ではない

### バージョニング手法の選択

| 手法 | 推奨度 | 理由 |
|------|--------|------|
| URLバージョニング | ⭐⭐⭐ | シンプル、明示的、デバッグが容易 |
| ヘッダーバージョニング | ⭐⭐ | RESTful、URLが変わらない |
| メディアタイプバージョニング | ⭐ | 複雑、一般的ではない |

**結論**: 特別な理由がない限り、URLバージョニングを推奨する。

## 下位互換性の維持

### 破壊的変更と非破壊的変更

#### 破壊的変更（Breakin Changes）

既存クライアントが動作しなくなる変更。新しいメジャーバージョンが必要。

**例**:
- 既存フィールドの削除
- 既存フィールドの型変更
- 既存フィールドの名前変更
- 必須フィールドの追加
- エンドポイントの削除
- HTTPメソッドの変更
- レスポンス構造の根本的な変更

**Before（v1）**:
```json
{
  "id": "plan_123",
  "title": "京都歴史探訪",
  "status": "planning"
}
```

**After（v2、破壊的変更）**:
```json
{
  "id": "plan_123",
  "name": "京都歴史探訪",  // titleからnameに変更（破壊的）
  "state": "planning"      // statusからstateに変更（破壊的）
}
```

#### 非破壊的変更（Non-breaking Changes）

既存クライアントが引き続き動作する変更。同一バージョン内で実装可能。

**例**:
- 新しいオプションフィールドの追加
- 新しいエンドポイントの追加
- エラーメッセージの改善
- レスポンスに新しいフィールドを追加
- 新しいHTTPメソッドの追加（既存メソッドは維持）

**Before（v1）**:
```json
{
  "id": "plan_123",
  "title": "京都歴史探訪",
  "status": "planning"
}
```

**After（v1、非破壊的変更）**:
```json
{
  "id": "plan_123",
  "title": "京都歴史探訪",
  "status": "planning",
  "tags": ["歴史", "文化"],           // 新しいフィールド（非破壊的）
  "estimated_duration_days": 3       // 新しいフィールド（非破壊的）
}
```

### フィールド追加のベストプラクティス

#### パターン1: オプションフィールドとして追加

既存フィールドは維持し、新しいフィールドを追加する。

**例**:
```python
# v1
class TravelPlanResponse(BaseModel):
    id: str
    title: str
    status: str

# v1（フィールド追加後）
class TravelPlanResponse(BaseModel):
    id: str
    title: str
    status: str
    tags: list[str] = []                  # 新しいフィールド（デフォルト値あり）
    estimated_duration_days: int | None = None  # 新しいフィールド（オプション）
```

#### パターン2: ネストされた詳細情報として追加

既存フィールドは維持し、詳細情報を別のフィールドに追加する。

**例**:
```python
# v1
class TravelPlanResponse(BaseModel):
    id: str
    title: str
    status: str

# v1（詳細情報追加後）
class StatusDetail(BaseModel):
    value: str
    updated_at: datetime
    updated_by: str

class TravelPlanResponse(BaseModel):
    id: str
    title: str
    status: str                           # 既存フィールド（維持）
    status_detail: StatusDetail | None = None  # 詳細情報（新規）
```

**レスポンス例**:
```json
{
  "id": "plan_123",
  "title": "京都歴史探訪",
  "status": "planning",
  "statusDetail": {
    "value": "planning",
    "updatedAt": "2025-01-30T10:00:00Z",
    "updatedBy": "user_123"
  }
}
```

### 非推奨（Deprecation）の扱い

将来削除予定のフィールドやエンドポイントは、非推奨（deprecated）としてマークする。

#### OpenAPIでの非推奨マーク

```python
@router.get(
    "/old-endpoint",
    deprecated=True,
    summary="旧エンドポイント（非推奨）",
    description="このエンドポイントは非推奨です。代わりに /new-endpoint を使用してください。",
)
def old_endpoint():
    ...
```

#### レスポンスヘッダーで警告

```python
@router.get("/old-endpoint")
def old_endpoint(response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-06-30"  # サポート終了日
    response.headers["Link"] = '</api/v1/new-endpoint>; rel="successor-version"'
    ...
```

#### ドキュメントでの告知

```markdown
## 非推奨API

以下のAPIは非推奨です。新しいAPIへの移行をお願いします。

| 旧エンドポイント | 新エンドポイント | 非推奨日 | 削除予定日 |
|----------------|----------------|---------|----------|
| GET /api/v1/old-endpoint | GET /api/v2/new-endpoint | 2025-12-31 | 2026-06-30 |
```

## バージョン移行戦略

### 段階的移行

1. **新バージョンリリース**: v2をリリース（v1は維持）
2. **移行期間の提供**: 十分な移行期間を設ける（例: 6ヶ月〜1年）
3. **非推奨マーク**: v1を非推奨としてマーク
4. **通知**: クライアントに移行を通知
5. **サポート終了告知**: v1のサポート終了日を告知
6. **削除**: サポート終了日にv1を削除

### 並行運用

複数バージョンを並行運用し、クライアントが段階的に移行できるようにする。

**例**:
```python
# v1（維持）
@v1_router.get("/travel-plans/{plan_id}")
def get_travel_plan_v1(plan_id: str):
    """旅行計画を取得する（v1）"""
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "status": "planning",
    }

# v2（新バージョン）
@v2_router.get("/travel-plans/{plan_id}")
def get_travel_plan_v2(plan_id: str):
    """旅行計画を取得する（v2）"""
    return {
        "id": plan_id,
        "title": "京都歴史探訪",
        "status": "planning",
        "statusDetail": {
            "value": "planning",
            "updatedAt": "2025-01-30T10:00:00Z",
            "updatedBy": "user_123"
        },
        "tags": ["歴史", "文化"],
    }
```

### バージョン間のコード共有

v1とv2で共通のビジネスロジックを共有し、レスポンス形式のみを変える。

```python
# 共通のユースケース
class GetTravelPlanUseCase:
    def execute(self, plan_id: str) -> TravelPlanDTO:
        ...

# v1エンドポイント
@v1_router.get("/travel-plans/{plan_id}")
def get_travel_plan_v1(plan_id: str):
    dto = use_case.execute(plan_id)
    # v1レスポンスに変換
    return TravelPlanResponseV1.from_dto(dto)

# v2エンドポイント
@v2_router.get("/travel-plans/{plan_id}")
def get_travel_plan_v2(plan_id: str):
    dto = use_case.execute(plan_id)
    # v2レスポンスに変換
    return TravelPlanResponseV2.from_dto(dto)
```

## バージョニングのタイミング

### メジャーバージョン（v1 → v2）

破壊的変更が必要な場合。

**例**:
- APIの根本的な再設計
- 認証方式の変更
- レスポンス構造の大幅な変更
- 複数の破壊的変更を一度に実施

### マイナーバージョン（v1.1 → v1.2）

非破壊的変更のみの場合（オプション）。

**例**:
- 新機能の追加
- 新しいエンドポイントの追加
- パフォーマンス改善

**注意**: URLバージョニングでは、通常マイナーバージョンは使用しない（`/api/v1.2/`とはしない）。マイナーバージョンは、非破壊的変更として同一バージョン内で実装する。

## 実装例: v1からv2への移行

### ステップ1: v2の実装

```python
# v2エンドポイント
@v2_router.post("/travel-plans", status_code=status.HTTP_201_CREATED)
def create_travel_plan_v2(request: CreateTravelPlanRequestV2):
    """旅行計画を作成する（v2）

    v2の変更点:
    - tagsフィールドを追加
    - estimatedDurationDaysフィールドを追加
    """
    use_case = CreateTravelPlanUseCase(repository)
    dto = use_case.execute(
        user_id=request.user_id,
        title=request.title,
        destination=request.destination,
        spots=spots_dict,
        tags=request.tags,  # v2で追加
        estimated_duration_days=request.estimated_duration_days,  # v2で追加
    )
    return TravelPlanResponseV2(**dto.__dict__)
```

### ステップ2: v1を非推奨としてマーク

```python
@v1_router.post(
    "/travel-plans",
    status_code=status.HTTP_201_CREATED,
    deprecated=True,
    description="このエンドポイントは非推奨です。v2を使用してください。サポート終了予定: 2026-06-30",
)
def create_travel_plan_v1(request: CreateTravelPlanRequestV1, response: Response):
    """旅行計画を作成する（v1、非推奨）"""
    # 非推奨ヘッダーを追加
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "2026-06-30"
    response.headers["Link"] = '</api/v2/travel-plans>; rel="successor-version"'

    use_case = CreateTravelPlanUseCase(repository)
    dto = use_case.execute(
        user_id=request.user_id,
        title=request.title,
        destination=request.destination,
        spots=spots_dict,
    )
    return TravelPlanResponseV1(**dto.__dict__)
```

### ステップ3: ドキュメント更新

```markdown
# API バージョニング

## 現在のバージョン

- **v2**: 最新バージョン（推奨）
- **v1**: 非推奨（サポート終了予定: 2026-06-30）

## v2の新機能

- tagsフィールドの追加
- estimatedDurationDaysフィールドの追加
- パフォーマンス改善

## 移行ガイド

v1からv2への移行方法については、[移行ガイド](migration-guide.md)を参照してください。
```

## まとめ

バージョニングと互換性のポイント:

1. **URLバージョニングを使用**: シンプルで明示的
2. **非破壊的変更を優先**: 可能な限り既存クライアントを破損させない
3. **段階的移行**: 十分な移行期間を提供
4. **非推奨マーク**: 削除予定のAPIは明確にマーク
5. **ドキュメント更新**: バージョン間の違いを明確に記載

これらの原則を守ることで、APIを進化させながら、既存クライアントとの互換性を維持できる。
