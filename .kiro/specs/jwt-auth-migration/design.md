# 設計書

## 概要

本ドキュメントは、Firebase JWT認証への移行に関する設計を定義します。現在のシステムでは、クライアントがリクエストボディやクエリパラメータで`user_id`を送信していますが、これをJWTトークンから取得した`uid`を使用する方式に変更します。

この変更により、以下のメリットが得られます：

1. **セキュリティの向上**: クライアントが任意の`user_id`を送信できなくなり、認証されたユーザーのみが自分のリソースにアクセス可能
2. **コードの簡潔化**: クライアント側で`userId`を管理・送信する必要がなくなる
3. **一貫性の向上**: 認証情報の単一ソース（JWTトークン）を使用

## アーキテクチャ

### 現在のフロー

```
クライアント → [JWT Token + user_id] → 認証ミドルウェア → エンドポイント
                                          ↓
                                    User_Context (uid)
                                          ↓
                                    リクエストのuser_idを使用（問題）
```

### 変更後のフロー

```
クライアント → [JWT Token のみ] → 認証ミドルウェア → エンドポイント
                                      ↓
                                User_Context (uid)
                                      ↓
                                auth.uidを使用（安全）
                                      ↓
                                所有者チェック（新規）
```

## コンポーネントとインターフェース

### バックエンド

#### 1. APIスキーマの変更

**変更対象ファイル**: `backend/app/interfaces/schemas/travel_plan.py`

**変更内容**:
- `CreateTravelPlanRequest`から`user_id`フィールドを削除
- バリデーターから`user_id`の検証を削除

**変更前**:
```python
class CreateTravelPlanRequest(BaseModel):
    user_id: str = Field(..., min_length=1, alias="userId", description="ユーザーID")
    title: str = Field(..., min_length=1, description="旅行タイトル")
    destination: str = Field(..., min_length=1, description="目的地")
    spots: list[TouristSpotSchema] = Field(default_factory=list, description="観光スポットリスト")

    @field_validator("user_id", "title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value
```

**変更後**:
```python
class CreateTravelPlanRequest(BaseModel):
    title: str = Field(..., min_length=1, description="旅行タイトル")
    destination: str = Field(..., min_length=1, description="目的地")
    spots: list[TouristSpotSchema] = Field(default_factory=list, description="観光スポットリスト")

    @field_validator("title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value
```

**変更対象ファイル**: `backend/app/interfaces/schemas/reflection.py`

**変更内容**:
- `CreateReflectionRequest`から`user_id`フィールドを削除
- バリデーターから`user_id`の検証を削除

**変更前**:
```python
class CreateReflectionRequest(BaseModel):
    plan_id: str = Field(..., min_length=1, alias="planId")
    user_id: str = Field(..., min_length=1, alias="userId")
    user_notes: str | None = Field(None, alias="userNotes")

    @field_validator("plan_id", "user_id")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value
```

**変更後**:
```python
class CreateReflectionRequest(BaseModel):
    plan_id: str = Field(..., min_length=1, alias="planId")
    user_notes: str | None = Field(None, alias="userNotes")

    @field_validator("plan_id")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be empty")
        return value
```

#### 2. エンドポイントの修正

**変更対象ファイル**: `backend/app/interfaces/api/v1/travel_plans.py`

**変更内容**:

1. **POST /travel-plans**: リクエストボディの`user_id`を削除し、`auth.uid`を使用
   - 変更箇所: `use_case.execute(user_id=auth.uid, ...)`（既に実装済み）

2. **GET /travel-plans**: クエリパラメータの`user_id`を削除し、`auth.uid`でフィルタ
   - 変更箇所: `use_case.execute(user_id=auth.uid)`（既に実装済み）

3. **GET /travel-plans/{plan_id}**: 所有者チェックを追加
   - 変更箇所: 取得後に`travel_plan.user_id == auth.uid`を検証

**変更前**:
```python
@router.get("/{plan_id}", response_model=TravelPlanResponse, summary="旅行計画を取得")
def get_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
    guide_repository: TravelGuideRepository = Depends(get_guide_repository),
    reflection_repository: ReflectionRepository = Depends(get_reflection_repository),
    auth: UserContext = Depends(require_auth),
) -> TravelPlanResponse:
    use_case = GetTravelPlanUseCase(
        repository,
        guide_repository=guide_repository,
        reflection_repository=reflection_repository,
    )
    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
```

**変更後**:
```python
@router.get("/{plan_id}", response_model=TravelPlanResponse, summary="旅行計画を取得")
def get_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
    guide_repository: TravelGuideRepository = Depends(get_guide_repository),
    reflection_repository: ReflectionRepository = Depends(get_reflection_repository),
    auth: UserContext = Depends(require_auth),
) -> TravelPlanResponse:
    use_case = GetTravelPlanUseCase(
        repository,
        guide_repository=guide_repository,
        reflection_repository=reflection_repository,
    )
    try:
        dto = use_case.execute(plan_id=plan_id)
        # 所有者チェック
        if dto.user_id != auth.uid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this travel plan.",
            )
        return TravelPlanResponse(**dto.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e
```

4. **PUT /travel-plans/{plan_id}**: 所有者チェックを追加
5. **DELETE /travel-plans/{plan_id}**: 所有者チェックを追加

**変更対象ファイル**: `backend/app/interfaces/api/v1/reflections.py`

**変更内容**:
- POST /reflections: リクエストボディの`user_id`を削除し、`auth.uid`を使用（既に実装済み）

**変更対象ファイル**: `backend/app/interfaces/api/v1/uploads.py`

**変更内容**:
- POST /spot-reflections: FormDataの`userId`を削除し、`auth.uid`を使用（既に実装済み）

**変更対象ファイル**: `backend/app/interfaces/api/v1/travel_guides.py`

**変更内容**:
- POST /travel-guides: 所有者チェックを追加

#### 3. 所有者チェックヘルパー関数

所有者チェックのロジックを共通化するため、ヘルパー関数を作成します。

**新規ファイル**: `backend/app/interfaces/api/v1/ownership.py`

```python
"""リソース所有者チェックヘルパー"""

from fastapi import HTTPException, status

from app.interfaces.middleware.auth import UserContext


def verify_ownership(resource_user_id: str, auth: UserContext, resource_type: str = "resource") -> None:
    """リソースの所有者を検証する
    
    Args:
        resource_user_id: リソースのuser_id
        auth: 認証ユーザーコンテキスト
        resource_type: リソースタイプ（エラーメッセージ用）
    
    Raises:
        HTTPException: 所有者でない場合は403エラー
    """
    if resource_user_id != auth.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You do not have permission to access this {resource_type}.",
        )
```

### フロントエンド

#### 1. 型定義の変更

**変更対象ファイル**: `frontend/src/types/travel.ts`

**変更内容**:
- `CreateTravelPlanRequest`から`userId`フィールドを削除

**変更前**:
```typescript
export interface CreateTravelPlanRequest {
  userId: string;
  title: string;
  destination: string;
  spots: TouristSpot[];
}
```

**変更後**:
```typescript
export interface CreateTravelPlanRequest {
  title: string;
  destination: string;
  spots: TouristSpot[];
}
```

**変更対象ファイル**: `frontend/src/types/reflection.ts`

**変更内容**:
- `CreateReflectionRequest`から`userId`フィールドを削除

**変更前**:
```typescript
export interface CreateReflectionRequest {
  planId: string;
  userId: string;
  userNotes?: string | null;
}
```

**変更後**:
```typescript
export interface CreateReflectionRequest {
  planId: string;
  userNotes?: string | null;
}
```

#### 2. APIクライアントの変更

**変更対象ファイル**: `frontend/src/lib/api.ts`

**変更内容**:

1. `SpotReflectionUploadRequest`型から`userId`を削除
2. `ApiClient`インターフェースから`userId`パラメータを削除
3. 各メソッドの実装から`userId`の処理を削除

**変更前**:
```typescript
export type SpotReflectionUploadRequest = {
  planId: string;
  userId: string;
  spotId: string;
  spotNote?: string;
  files: File[];
  signal?: AbortSignal;
};

export type ApiClient = {
  listTravelPlans: (params: {
    userId: string;
    signal?: AbortSignal;
  }) => Promise<TravelPlanListResponse[]>;
  // ...
};
```

**変更後**:
```typescript
export type SpotReflectionUploadRequest = {
  planId: string;
  spotId: string;
  spotNote?: string;
  files: File[];
  signal?: AbortSignal;
};

export type ApiClient = {
  listTravelPlans: (params: {
    signal?: AbortSignal;
  }) => Promise<TravelPlanListResponse[]>;
  // ...
};
```

**メソッド実装の変更**:

```typescript
// listTravelPlans
listTravelPlans: async ({ signal }) => {
  return request<TravelPlanListResponse[]>({
    method: 'GET',
    path: '/travel-plans',
    signal,
  });
},

// createTravelPlan
createTravelPlan: async ({ request: payload, signal }) => {
  assertNonEmpty(payload.title, 'title');
  assertNonEmpty(payload.destination, 'destination');
  return request<TravelPlanResponse, CreateTravelPlanRequest>({
    method: 'POST',
    path: '/travel-plans',
    body: payload,
    signal,
  });
},

// createReflection
createReflection: async ({ request: payload, signal }) => {
  assertNonEmpty(payload.planId, 'planId');
  if (payload.userNotes !== undefined && payload.userNotes !== null) {
    assertNonEmpty(payload.userNotes, 'userNotes');
  }
  return request<void, CreateReflectionRequest>({
    method: 'POST',
    path: '/reflections',
    body: payload,
    signal,
    responseType: 'void',
  });
},

// uploadSpotReflection
uploadSpotReflection: async ({ planId, spotId, spotNote, files, signal }) => {
  assertNonEmpty(planId, 'planId');
  assertNonEmpty(spotId, 'spotId');
  assertNonEmptyFiles(files);

  const formData = new FormData();
  formData.append('planId', planId);
  formData.append('spotId', spotId);
  if (spotNote?.trim()) {
    formData.append('spotNote', spotNote);
  }
  for (const file of files) {
    formData.append('files', file);
  }

  return request<void, FormData>({
    method: 'POST',
    path: '/spot-reflections',
    body: formData,
    signal,
    responseType: 'void',
  });
},
```

#### 3. コンポーネントの変更

**変更対象ファイル**:
- `frontend/src/app/travel/page.tsx`
- `frontend/src/app/travel/new/page.tsx`
- `frontend/src/app/reflection/page.tsx`
- `frontend/src/app/reflection/[id]/page.tsx`

**変更内容**:
- APIクライアント呼び出しから`userId`パラメータを削除
- リクエストオブジェクトから`userId`フィールドを削除

**変更例** (`frontend/src/app/travel/page.tsx`):

**変更前**:
```typescript
const userId = user.uid;
const response = await apiClient.listTravelPlans({ userId });
```

**変更後**:
```typescript
const response = await apiClient.listTravelPlans({});
```

**変更例** (`frontend/src/app/travel/new/page.tsx`):

**変更前**:
```typescript
const userId = user?.uid ?? '';
const response = await apiClient.createTravelPlan({
  request: {
    userId,
    title: title.trim(),
    destination: destination.trim(),
    spots: validSpots,
  },
});
```

**変更後**:
```typescript
const response = await apiClient.createTravelPlan({
  request: {
    title: title.trim(),
    destination: destination.trim(),
    spots: validSpots,
  },
});
```

#### 4. テストの更新

**変更対象ファイル**:
- すべてのテストファイルで`userId`を使用している箇所

**変更内容**:
- モックデータから`userId`の削除は不要（レスポンスには含まれる）
- APIクライアント呼び出しのモックから`userId`パラメータを削除

## データモデル

データベーススキーマは変更しません。`user_id`カラムは引き続き使用されます。

**変更なし**:
- `travel_plans`テーブルの`user_id`カラム
- `reflections`テーブルの`user_id`カラム
- その他のテーブルの`user_id`カラム

## 正確性プロパティ

*プロパティとは、システムのすべての有効な実行において真であるべき特性や振る舞いのことです。プロパティは、人間が読める仕様と機械が検証可能な正確性保証の橋渡しとなります。*

### バックエンドプロパティ

#### プロパティ1: 旅行計画作成時のauth.uid使用

*すべての*有効な旅行計画作成リクエストに対して、作成された旅行計画の`user_id`は`auth.uid`と等しくなければならない

**検証**: 要件2.1

#### プロパティ2: 旅行計画一覧のフィルタリング

*すべての*旅行計画一覧取得リクエストに対して、返されるすべての旅行計画の`user_id`は`auth.uid`と等しくなければならない

**検証**: 要件2.2

#### プロパティ3: 振り返り作成時のauth.uid使用

*すべての*有効な振り返り作成リクエストに対して、作成された振り返りの`user_id`は`auth.uid`と等しくなければならない

**検証**: 要件2.3

#### プロパティ4: スポット振り返りアップロード時のauth.uid使用

*すべての*有効なスポット振り返りアップロードリクエストに対して、作成された振り返りの`user_id`は`auth.uid`と等しくなければならない

**検証**: 要件2.4

#### プロパティ5: 旅行計画取得時の所有者チェック

*すべての*旅行計画取得リクエストに対して、取得された旅行計画の`user_id`が`auth.uid`と等しくない場合、システムは403 Forbiddenエラーを返さなければならない

**検証**: 要件3.1

#### プロパティ6: 旅行計画更新時の所有者チェック

*すべての*旅行計画更新リクエストに対して、更新対象の旅行計画の`user_id`が`auth.uid`と等しくない場合、システムは403 Forbiddenエラーを返さなければならない

**検証**: 要件3.2

#### プロパティ7: 旅行計画削除時の所有者チェック

*すべての*旅行計画削除リクエストに対して、削除対象の旅行計画の`user_id`が`auth.uid`と等しくない場合、システムは403 Forbiddenエラーを返さなければならない

**検証**: 要件3.3

#### プロパティ8: 旅行ガイド生成時の所有者チェック

*すべての*旅行ガイド生成リクエストに対して、対象の旅行計画の`user_id`が`auth.uid`と等しくない場合、システムは403 Forbiddenエラーを返さなければならない

**検証**: 要件3.4

#### プロパティ9: リクエストボディにuser_idが不要

*すべての*APIリクエストに対して、リクエストボディまたはクエリパラメータに`user_id`が含まれていなくても、リクエストは成功しなければならない

**検証**: 要件1.3

### フロントエンドプロパティ

#### プロパティ10: listTravelPlansがuserIdを要求しない

*すべての*`listTravelPlans`メソッド呼び出しに対して、`userId`パラメータなしで呼び出しが成功しなければならない

**検証**: 要件5.1

#### プロパティ11: createTravelPlanがuserIdを含めない

*すべての*`createTravelPlan`メソッド呼び出しに対して、送信されるリクエストボディに`userId`フィールドが含まれていてはならない

**検証**: 要件5.2

#### プロパティ12: createReflectionがuserIdを含めない

*すべての*`createReflection`メソッド呼び出しに対して、送信されるリクエストボディに`userId`フィールドが含まれていてはならない

**検証**: 要件5.3

#### プロパティ13: uploadSpotReflectionがuserIdを含めない

*すべての*`uploadSpotReflection`メソッド呼び出しに対して、送信されるFormDataに`userId`フィールドが含まれていてはならない

**検証**: 要件5.4

#### プロパティ14: Authorizationヘッダーの設定

*すべての*APIリクエストに対して、Authorizationヘッダーに`Bearer {token}`形式のJWTトークンが含まれていなければならない

**検証**: 要件5.5

## エラーハンドリング

### 1. 認証エラー（401 Unauthorized）

**発生条件**:
- JWTトークンが欠落している
- JWTトークンが無効または期限切れ

**処理**:
- 既存の認証ミドルウェア（`require_auth`）が処理
- 変更なし

### 2. 権限エラー（403 Forbidden）

**発生条件**:
- リソースの所有者でないユーザーがアクセスを試みた

**処理**:
- 所有者チェックで検出
- HTTPException(status_code=403, detail="You do not have permission to access this {resource_type}.")を返す

**エラーレスポンス例**:
```json
{
  "error": {
    "type": "ForbiddenError",
    "message": "You do not have permission to access this travel plan."
  }
}
```

### 3. リソース未検出エラー（404 Not Found）

**発生条件**:
- 指定されたIDのリソースが存在しない

**処理**:
- 既存のエラーハンドリングを維持
- 所有者チェックの前にリソースの存在を確認

**注意**: 404エラーと403エラーの順序は重要です。リソースが存在しない場合は404を返し、存在するが所有者でない場合は403を返します。

## テスト戦略

### デュアルテストアプローチ

本プロジェクトでは、ユニットテストとプロパティベーステストの両方を使用します：

- **ユニットテスト**: 特定の例、エッジケース、エラー条件を検証
- **プロパティベーステスト**: すべての入力に対する普遍的なプロパティを検証

両者は補完的であり、包括的なカバレッジを実現します。

### バックエンドテスト

#### ユニットテスト（pytest）

**テスト対象**:
1. APIスキーマのバリデーション
   - `user_id`フィールドが存在しないことを確認
   - 他のフィールドのバリデーションが正常に動作することを確認

2. エンドポイントの動作
   - `auth.uid`が正しく使用されることを確認
   - 所有者チェックが正常に動作することを確認
   - 403エラーが正しく返されることを確認

3. エッジケース
   - 認証トークンが欠落している場合
   - 無効な認証トークンの場合
   - 存在しないリソースへのアクセス

**テストファイル**:
- `backend/tests/interfaces/api/v1/test_travel_plans.py`
- `backend/tests/interfaces/api/v1/test_reflections.py`
- `backend/tests/interfaces/api/v1/test_uploads.py`
- `backend/tests/interfaces/api/v1/test_travel_guides.py`

#### プロパティベーステスト（Hypothesis）

**設定**:
- 最小100回の反復実行
- 各テストにはデザインドキュメントのプロパティを参照するタグを付与
- タグ形式: **Feature: jwt-auth-migration, Property {number}: {property_text}**

**テスト対象**:
- プロパティ1-9の検証

**テストファイル**:
- `backend/tests/properties/test_jwt_auth_properties.py`

### フロントエンドテスト

#### ユニットテスト（Vitest）

**テスト対象**:
1. APIクライアントの動作
   - `userId`パラメータが送信されないことを確認
   - リクエストボディに`userId`が含まれないことを確認
   - Authorizationヘッダーが正しく設定されることを確認

2. コンポーネントの動作
   - APIクライアント呼び出しが正しいパラメータで行われることを確認
   - エラーハンドリングが正常に動作することを確認

**テストファイル**:
- `frontend/src/lib/api.test.ts`
- `frontend/src/app/travel/page.test.tsx`
- `frontend/src/app/travel/new/page.test.tsx`
- `frontend/src/app/reflection/page.test.tsx`
- `frontend/src/app/reflection/[id]/page.test.tsx`

#### プロパティベーステスト（fast-check）

**設定**:
- 最小100回の反復実行
- 各テストにはデザインドキュメントのプロパティを参照するタグを付与

**テスト対象**:
- プロパティ8, 9の検証

**テストファイル**:
- `frontend/src/lib/api.property.test.ts`

### 統合テスト

**テスト対象**:
1. エンドツーエンドのフロー
   - 認証 → リソース作成 → リソース取得 → リソース更新 → リソース削除
   - 他のユーザーのリソースへのアクセス試行

2. エラーシナリオ
   - 認証なしでのアクセス
   - 無効なトークンでのアクセス
   - 他のユーザーのリソースへのアクセス

**テストファイル**:
- `backend/tests/integration/test_jwt_auth_flow.py`

## OpenAPI仕様の更新

**変更対象ファイル**: `docs/backend/openapi.json`

**変更内容**:
1. `CreateTravelPlanRequest`スキーマから`user_id`を削除
2. `CreateReflectionRequest`スキーマから`user_id`を削除
3. 各エンドポイントに403レスポンスを追加

**403レスポンススキーマ**:
```json
{
  "403": {
    "description": "Forbidden - You do not have permission to access this resource",
    "content": {
      "application/json": {
        "schema": {
          "type": "object",
          "properties": {
            "error": {
              "type": "object",
              "properties": {
                "type": { "type": "string", "example": "ForbiddenError" },
                "message": { "type": "string", "example": "You do not have permission to access this travel plan." }
              }
            }
          }
        }
      }
    }
  }
}
```

## 実装の注意点

### 1. 段階的な移行

実装は以下の順序で行います：

1. バックエンドのスキーマ変更
2. バックエンドのエンドポイント修正（所有者チェック追加）
3. バックエンドのテスト更新
4. フロントエンドの型定義変更
5. フロントエンドのAPIクライアント変更
6. フロントエンドのコンポーネント変更
7. フロントエンドのテスト更新
8. OpenAPI仕様の更新

### 2. 後方互換性

この変更は破壊的変更です。バックエンドとフロントエンドは同時にデプロイする必要があります。

### 3. 既存データへの影響

データベーススキーマは変更しないため、既存データへの影響はありません。

### 4. パフォーマンスへの影響

所有者チェックにより、各リクエストで追加のデータベースクエリが発生する可能性がありますが、ほとんどの場合、リソース取得時に既にデータを取得しているため、追加のクエリは不要です。

### 5. セキュリティ考慮事項

- JWTトークンの検証は既存の認証ミドルウェアで行われます
- 所有者チェックは必ずリソース取得後に行います
- エラーメッセージは情報漏洩を防ぐため、一般的な内容にします
