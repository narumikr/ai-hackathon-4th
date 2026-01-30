# リソース指向設計

## 概要

リソース指向設計は、RESTful APIの基本原則である。APIはリソース（データやオブジェクト）を中心に設計し、URIでリソースを識別し、HTTPメソッドでリソースに対する操作を表現する。

## リソースの特定方法

### リソースとは

リソースは、APIで扱うデータやオブジェクトの抽象概念である。例:

- ユーザー（User）
- 旅行計画（TravelPlan）
- 注文（Order）
- 記事（Article）

### リソースの特定手順

1. **ドメインモデルを分析**: ビジネスロジックで扱うエンティティを洗い出す
2. **主要なリソースを抽出**: CRUD操作が必要なエンティティを特定
3. **リレーションシップを整理**: リソース間の関係（1対多、多対多など）を明確化
4. **サブリソースを検討**: 親リソースに依存する子リソースを識別

### 例: 旅行計画システム

**主要リソース**:
- `TravelPlan`（旅行計画）
- `TravelGuide`（旅行ガイド）
- `Reflection`（振り返り）

**リレーションシップ**:
- 1つの旅行計画は複数のガイドを持つ（1対多）
- 1つの旅行計画は1つの振り返りを持つ（1対1）

## URI設計の詳細ルール

### 1. 複数形の名詞を使用

**理由**: コレクション（複数のリソース）と個別リソースの一貫性を保つ。

**推奨**:
```
GET /api/v1/travel-plans           # コレクション
GET /api/v1/travel-plans/{plan_id} # 個別リソース
```

**非推奨**:
```
GET /api/v1/travel-plan            # 単数形（×）
GET /api/v1/travel-plans/{plan_id} # 複数形と混在（×）
```

### 2. ケバブケース（kebab-case）を使用

**理由**: URLは大文字小文字を区別しない環境もあるため、小文字のみを使用する。単語の区切りにはハイフンを使用。

**推奨**:
```
/api/v1/travel-plans
/api/v1/tourist-spots
/api/v1/user-profiles
```

**非推奨**:
```
/api/v1/travel_plans   # スネークケース（Pythonバックエンドでも×）
/api/v1/travelPlans    # キャメルケース（×）
/api/v1/TravelPlans    # パスカルケース（×）
```

**注意**: プロジェクトによっては、既存のコードベースでスネークケースが使用されている場合もある。その場合は一貫性を優先する。

### 3. 動詞を避ける

**理由**: HTTPメソッドが操作を表現するため、URIには名詞のみを含める。

**推奨**:
```
GET    /api/v1/travel-plans/{plan_id}  # 取得
POST   /api/v1/travel-plans             # 作成
PUT    /api/v1/travel-plans/{plan_id}  # 更新
DELETE /api/v1/travel-plans/{plan_id}  # 削除
```

**非推奨**:
```
GET    /api/v1/get-travel-plan/{plan_id}    # 動詞を含む（×）
POST   /api/v1/create-travel-plan           # 動詞を含む（×）
POST   /api/v1/travel-plans/update/{plan_id} # 動詞を含む（×）
DELETE /api/v1/delete-travel-plan/{plan_id} # 動詞を含む（×）
```

**例外**: CRUD操作に該当しないアクション（検索、集計、バッチ処理など）では動詞を使用する場合もある。

```
POST /api/v1/travel-plans/search   # 検索（複雑なフィルタ条件の場合）
POST /api/v1/users/reset-password  # パスワードリセット
```

### 4. パス構造のベストプラクティス

#### 階層は2階層まで推奨

**推奨**（1階層）:
```
GET /api/v1/travel-plans
GET /api/v1/travel-plans/{plan_id}
```

**推奨**（2階層）:
```
GET /api/v1/travel-plans/{plan_id}/guides
GET /api/v1/travel-plans/{plan_id}/guides/{guide_id}
```

**非推奨**（3階層以上）:
```
GET /api/v1/users/{user_id}/travel-plans/{plan_id}/guides/{guide_id}/sections/{section_id}
```

**理由**: 深いネストはURIが長くなり、APIが使いにくくなる。

**代替案**: サブリソースIDで直接アクセス。
```
GET /api/v1/guides/{guide_id}/sections/{section_id}
```

#### パスパラメータとクエリパラメータの使い分け

**パスパラメータ**: リソースの識別に使用。
```
GET /api/v1/travel-plans/{plan_id}
```

**クエリパラメータ**: フィルタリング、ソート、ページネーションに使用。
```
GET /api/v1/travel-plans?user_id=user_123&status=planning&sort=-created_at&limit=20&offset=0
```

## クエリパラメータの使用

### フィルタリング

リソースのフィールド名をそのままパラメータ名に使用。

```
GET /api/v1/travel-plans?user_id=user_123
GET /api/v1/travel-plans?status=planning
GET /api/v1/travel-plans?user_id=user_123&status=planning
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

### ソート

`sort`パラメータを使用し、降順はマイナス記号（`-`）をプレフィックスに付ける。

```
GET /api/v1/travel-plans?sort=created_at      # 昇順
GET /api/v1/travel-plans?sort=-created_at     # 降順
GET /api/v1/travel-plans?sort=status,-created_at  # 複数フィールド
```

### ページネーション

詳細は`pagination-filtering-sorting.md`を参照。

```
GET /api/v1/travel-plans?limit=20&offset=0
GET /api/v1/travel-plans?page=1&page_size=20
```

## リレーションシップの表現

### 1対多のリレーションシップ

#### パターン1: サブリソースとして表現

親リソースに依存する子リソースの場合。

```
GET /api/v1/travel-plans/{plan_id}/guides
GET /api/v1/travel-plans/{plan_id}/guides/{guide_id}
```

**使用ケース**:
- 子リソースが親リソースに強く依存する
- 子リソースが親リソースのコンテキストでのみ意味を持つ

#### パターン2: 独立したリソースとして表現

子リソースが独立して存在できる場合。

```
GET /api/v1/guides?travel_plan_id=plan_123
GET /api/v1/guides/{guide_id}
```

**使用ケース**:
- 子リソースが複数の親リソースに関連する可能性がある
- 子リソースが独立したライフサイクルを持つ

#### パターン3: レスポンスに埋め込む

関連リソースを親リソースのレスポンスに含める。

```json
GET /api/v1/travel-plans/{plan_id}

{
  "id": "plan_123",
  "title": "京都歴史探訪",
  "destination": "京都",
  "status": "planning",
  "guide": {
    "id": "guide_456",
    "title": "京都の歴史ガイド",
    "content": "..."
  }
}
```

**使用ケース**:
- 関連リソースが常に一緒に取得される
- N+1問題を避けたい

**プロジェクト実装例**:
```python
# backend/app/interfaces/schemas/travel_plan.py:110-127
class TravelPlanResponse(BaseModel):
    id: str
    user_id: str = Field(..., alias="userId")
    title: str
    destination: str
    spots: list[TouristSpotSchema]
    status: str
    guide_generation_status: str = Field(..., alias="guideGenerationStatus")
    reflection_generation_status: str = Field(..., alias="reflectionGenerationStatus")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    guide: TravelGuideResponse | None = None
    reflection: ReflectionResponse | None = None
    pamphlet: ReflectionPamphletResponse | None = None
```

### 多対多のリレーションシップ

中間リソースとして表現する。

**例**: タグとブログ記事の多対多リレーション。

```
# 記事に付与されたタグ一覧
GET /api/v1/articles/{article_id}/tags

# タグが付与された記事一覧
GET /api/v1/tags/{tag_id}/articles

# タグの追加/削除
POST   /api/v1/articles/{article_id}/tags
DELETE /api/v1/articles/{article_id}/tags/{tag_id}
```

## コレクションとシングルトンリソース

### コレクションリソース

複数のリソースを含む。

```
GET  /api/v1/travel-plans       # 一覧取得
POST /api/v1/travel-plans       # 新規作成
```

### シングルトンリソース

単一のリソースのみを表す。

```
GET   /api/v1/users/{user_id}/profile  # ユーザープロフィール取得
PUT   /api/v1/users/{user_id}/profile  # ユーザープロフィール更新
```

**特徴**:
- IDパラメータを含まない
- 親リソースに対して1つだけ存在する

## リソース命名規則

### 一般的な命名パターン

| リソース種別 | 命名パターン | 例 |
|-------------|-------------|-----|
| エンティティ | 複数形の名詞 | `users`, `travel-plans`, `orders` |
| サブリソース | 親リソース + 複数形の名詞 | `travel-plans/{id}/guides` |
| シングルトン | 単数形の名詞 | `profile`, `settings` |
| アクション | 動詞 | `search`, `export`, `reset-password` |

### 命名の一貫性

プロジェクト全体で一貫したケーススタイルを使用する。

**推奨**: すべてのURIパスをケバブケース（kebab-case）で統一。
```
/api/v1/travel-plans
/api/v1/travel-guides
/api/v1/user-profiles
```

**非推奨**: 混在させない。
```
/api/v1/travel-plans    # ケバブケース
/api/v1/travel_guides   # スネークケース（混在）
/api/v1/userProfiles    # キャメルケース（混在）
```

## Before/After実例

### 例1: 旅行計画API

**Before**（悪い設計）:
```
GET  /api/getTravelPlans?userId=user_123
POST /api/addTravelPlan
GET  /api/getTravelPlan?planId=plan_123
POST /api/updateTravelPlan?planId=plan_123
POST /api/deleteTravelPlan?planId=plan_123
```

**After**（良い設計）:
```
GET    /api/v1/travel-plans?user_id=user_123
POST   /api/v1/travel-plans
GET    /api/v1/travel-plans/{plan_id}
PUT    /api/v1/travel-plans/{plan_id}
DELETE /api/v1/travel-plans/{plan_id}
```

**改善ポイント**:
- リソース名を複数形の名詞に変更
- HTTPメソッドで操作を表現（URIから動詞を削除）
- パスパラメータで個別リソースを識別
- クエリパラメータでフィルタリング
- バージョニングを追加（`/api/v1/`）

### 例2: ブログAPI

**Before**（悪い設計）:
```
GET  /api/posts/getAll
GET  /api/posts/getById/123
POST /api/posts/create
POST /api/posts/123/update
POST /api/posts/123/delete
GET  /api/posts/123/comments/getAll
POST /api/posts/123/comments/add
```

**After**（良い設計）:
```
GET    /api/v1/posts
GET    /api/v1/posts/{post_id}
POST   /api/v1/posts
PUT    /api/v1/posts/{post_id}
DELETE /api/v1/posts/{post_id}
GET    /api/v1/posts/{post_id}/comments
POST   /api/v1/posts/{post_id}/comments
```

**改善ポイント**:
- URIから動詞を削除
- HTTPメソッドで操作を表現
- サブリソース（comments）を階層構造で表現
- 一貫したパスパラメータの使用

## まとめ

リソース指向設計のポイント:

1. **リソースを名詞で表現**: 動詞を避け、複数形の名詞を使用
2. **HTTPメソッドで操作を表現**: GET、POST、PUT、PATCH、DELETE
3. **階層は2階層まで**: 深いネストを避ける
4. **一貫したケーススタイル**: ケバブケース推奨
5. **リレーションシップを適切に表現**: サブリソース、埋め込み、独立リソース
6. **パスパラメータとクエリパラメータを使い分け**: 識別 vs フィルタリング

これらの原則を守ることで、直感的で使いやすいAPIを設計できる。
