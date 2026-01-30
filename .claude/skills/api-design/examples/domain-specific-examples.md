# ドメイン別API設計例

## 概要

ドメインごとの具体的なAPI設計例を示す。各ドメインの特性に応じたベストプラクティスを適用する。

## 1. ユーザー管理API

### リソース設計

```
/api/v1/users                    # ユーザー一覧
/api/v1/users/{user_id}          # 個別ユーザー
/api/v1/users/{user_id}/profile  # ユーザープロフィール（シングルトン）
/api/v1/users/{user_id}/settings # ユーザー設定（シングルトン）
```

### エンドポイント例

```python
# ユーザー作成
@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(request: CreateUserRequest):
    """新しいユーザーを作成する"""
    ...

# ユーザー一覧取得
@router.get("/users", response_model=PaginatedUserResponse)
def list_users(
    email: str | None = None,
    role: list[str] = Query([]),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """ユーザー一覧を取得する（フィルタ・ページネーション付き）"""
    ...

# ユーザー取得
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    """ユーザーを取得する"""
    ...

# プロフィール更新（シングルトン）
@router.put("/users/{user_id}/profile", response_model=ProfileResponse)
def update_profile(user_id: str, request: UpdateProfileRequest):
    """ユーザープロフィールを更新する"""
    ...

# パスワード変更（アクション）
@router.post("/users/{user_id}/password/reset")
def reset_password(user_id: str, request: ResetPasswordRequest):
    """パスワードをリセットする"""
    ...
```

### レスポンス例

```json
{
  "id": "user_123",
  "email": "user@example.com",
  "name": "田中太郎",
  "role": "admin",
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-30T10:00:00Z",
  "profile": {
    "avatar": "https://example.com/avatar.jpg",
    "bio": "エンジニア"
  }
}
```

## 2. Eコマース注文API

### リソース設計

```
/api/v1/orders                      # 注文一覧
/api/v1/orders/{order_id}           # 個別注文
/api/v1/orders/{order_id}/items     # 注文アイテム
/api/v1/orders/{order_id}/payment   # 支払い情報
/api/v1/orders/{order_id}/shipment  # 配送情報
```

### エンドポイント例

```python
# 注文作成
@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(request: CreateOrderRequest):
    """新しい注文を作成する"""
    ...

# 注文一覧取得
@router.get("/orders", response_model=PaginatedOrderResponse)
def list_orders(
    user_id: str | None = None,
    status: list[str] = Query([]),
    created_at_gte: datetime | None = None,
    created_at_lte: datetime | None = None,
    sort: str = "-created_at",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """注文一覧を取得する（フィルタ・ページネーション付き）"""
    ...

# 注文ステータス更新（部分更新）
@router.patch("/orders/{order_id}", response_model=OrderResponse)
def update_order_status(order_id: str, request: UpdateOrderStatusRequest):
    """注文ステータスを更新する"""
    ...

# 注文キャンセル（アクション）
@router.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, request: CancelOrderRequest):
    """注文をキャンセルする"""
    ...
```

### レスポンス例

```json
{
  "id": "order_123",
  "userId": "user_123",
  "status": "shipped",
  "totalAmount": 10000,
  "items": [
    {
      "id": "item_1",
      "productId": "prod_456",
      "quantity": 2,
      "price": 5000
    }
  ],
  "payment": {
    "method": "credit_card",
    "status": "paid",
    "paidAt": "2025-01-30T10:00:00Z"
  },
  "shipment": {
    "status": "in_transit",
    "trackingNumber": "1234567890",
    "estimatedDelivery": "2025-02-05"
  },
  "createdAt": "2025-01-30T09:00:00Z",
  "updatedAt": "2025-01-30T10:00:00Z"
}
```

## 3. ブログ/CMS API

### リソース設計

```
/api/v1/posts                       # 記事一覧
/api/v1/posts/{post_id}             # 個別記事
/api/v1/posts/{post_id}/comments    # 記事のコメント
/api/v1/categories                  # カテゴリ一覧
/api/v1/tags                        # タグ一覧
```

### エンドポイント例

```python
# 記事作成
@router.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(request: CreatePostRequest):
    """新しい記事を作成する"""
    ...

# 記事一覧取得
@router.get("/posts", response_model=PaginatedPostResponse)
def list_posts(
    category_id: str | None = None,
    tag_id: list[str] = Query([]),
    status: str | None = None,
    author_id: str | None = None,
    published_at_gte: datetime | None = None,
    search: str | None = None,  # タイトル・本文の全文検索
    sort: str = "-published_at",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """記事一覧を取得する（フィルタ・検索・ページネーション付き）"""
    ...

# 記事公開（アクション）
@router.post("/posts/{post_id}/publish")
def publish_post(post_id: str, request: PublishPostRequest):
    """記事を公開する"""
    ...

# コメント追加
@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(post_id: str, request: AddCommentRequest):
    """記事にコメントを追加する"""
    ...
```

### レスポンス例

```json
{
  "id": "post_123",
  "title": "RESTful API設計のベストプラクティス",
  "slug": "restful-api-best-practices",
  "content": "...",
  "excerpt": "RESTful API設計の基本原則を解説します。",
  "status": "published",
  "authorId": "user_123",
  "categoryId": "cat_456",
  "tags": ["API", "REST", "設計"],
  "publishedAt": "2025-01-30T10:00:00Z",
  "createdAt": "2025-01-29T10:00:00Z",
  "updatedAt": "2025-01-30T10:00:00Z",
  "commentsCount": 5
}
```

## 4. 旅行計画API（プロジェクト関連）

### リソース設計

```
/api/v1/travel-plans                        # 旅行計画一覧
/api/v1/travel-plans/{plan_id}              # 個別旅行計画
/api/v1/travel-plans/{plan_id}/guides       # 旅行ガイド
/api/v1/travel-plans/{plan_id}/reflections  # 振り返り
```

### エンドポイント例

既存実装をベースにした設計例。

```python
# 旅行計画作成
@router.post(
    "/travel-plans",
    response_model=TravelPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="旅行計画を作成",
)
def create_travel_plan(request: CreateTravelPlanRequest):
    """旅行計画を作成する

    Args:
        request: 旅行計画作成リクエスト
            - user_id: ユーザーID
            - title: 旅行タイトル
            - destination: 目的地
            - spots: 観光スポットリスト

    Returns:
        TravelPlanResponse: 作成された旅行計画

    Raises:
        HTTPException: バリデーションエラー（400）
    """
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


# 旅行計画一覧取得
@router.get(
    "/travel-plans",
    response_model=list[TravelPlanListResponse],
    summary="旅行計画一覧を取得",
)
def list_travel_plans(
    user_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
):
    """ユーザーの旅行計画一覧を取得する

    Args:
        user_id: ユーザーID

    Returns:
        list[TravelPlanListResponse]: 旅行計画リスト
    """
    use_case = ListTravelPlansUseCase(repository)
    try:
        dtos = use_case.execute(user_id=user_id)
        return [TravelPlanListResponse.from_dto(dto) for dto in dtos]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# 旅行計画取得
@router.get(
    "/travel-plans/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を取得",
)
def get_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
    guide_repository: TravelGuideRepository = Depends(get_guide_repository),
    reflection_repository: ReflectionRepository = Depends(get_reflection_repository),
):
    """旅行計画を取得する（関連ガイド・振り返りを含む）

    Args:
        plan_id: 旅行計画ID

    Returns:
        TravelPlanResponse: 旅行計画（guide、reflectionフィールドを含む）

    Raises:
        HTTPException: 旅行計画が見つからない（404）
    """
    use_case = GetTravelPlanUseCase(
        repository,
        guide_repository=guide_repository,
        reflection_repository=reflection_repository,
    )

    try:
        dto = use_case.execute(plan_id=plan_id)
        return TravelPlanResponse(**dto.__dict__)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except TravelPlanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Travel plan not found: {plan_id}",
        ) from e


# 旅行計画更新
@router.put(
    "/travel-plans/{plan_id}",
    response_model=TravelPlanResponse,
    summary="旅行計画を更新",
)
def update_travel_plan(
    plan_id: str,
    request: UpdateTravelPlanRequest,
    repository: TravelPlanRepository = Depends(get_repository),
):
    """旅行計画を更新する

    Args:
        plan_id: 旅行計画ID
        request: 旅行計画更新リクエスト
            - title: 旅行タイトル（オプション）
            - destination: 目的地（オプション）
            - spots: 観光スポットリスト（オプション）
            - status: 旅行状態（オプション）

    Returns:
        TravelPlanResponse: 更新された旅行計画

    Raises:
        HTTPException: 旅行計画が見つからない（404）、バリデーションエラー（400）
    """
    use_case = UpdateTravelPlanUseCase(repository)

    spots_dict = None
    if request.spots is not None:
        spots_dict = [spot.model_dump(by_alias=True) for spot in request.spots]

    try:
        dto = use_case.execute(
            plan_id=plan_id,
            title=request.title,
            destination=request.destination,
            spots=spots_dict,
            status=request.status,
        )
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


# 旅行計画削除
@router.delete(
    "/travel-plans/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="旅行計画を削除",
)
def delete_travel_plan(
    plan_id: str,
    repository: TravelPlanRepository = Depends(get_repository),
):
    """旅行計画を削除する

    Args:
        plan_id: 旅行計画ID

    Returns:
        Response: 204 No Content

    Raises:
        HTTPException: 旅行計画が見つからない（404）
    """
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

### リクエストスキーマ

```python
class TouristSpotSchema(BaseModel):
    """観光スポットスキーマ"""
    id: str | None = Field(None, description="スポットID")
    name: str = Field(..., min_length=1, description="スポット名")
    description: str | None = Field(None, description="説明")
    user_notes: str | None = Field(None, alias="userNotes", description="ユーザーメモ")

    model_config = {"populate_by_name": True}


class CreateTravelPlanRequest(BaseModel):
    """旅行計画作成リクエスト"""
    user_id: str = Field(..., min_length=1, alias="userId", description="ユーザーID")
    title: str = Field(..., min_length=1, description="旅行タイトル")
    destination: str = Field(..., min_length=1, description="目的地")
    spots: list[TouristSpotSchema] = Field(default_factory=list, description="観光スポットリスト")

    model_config = {"populate_by_name": True}

    @field_validator("user_id", "title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """空文字列でないことを検証する"""
        if not value.strip():
            raise ValueError("must not be empty")
        return value


class UpdateTravelPlanRequest(BaseModel):
    """旅行計画更新リクエスト"""
    title: str | None = Field(None, min_length=1, description="旅行タイトル")
    destination: str | None = Field(None, min_length=1, description="目的地")
    spots: list[TouristSpotSchema] | None = Field(None, description="観光スポットリスト")
    status: str | None = Field(None, description="旅行状態")

    @field_validator("title", "destination")
    @classmethod
    def validate_not_empty(cls, value: str | None) -> str | None:
        """空文字列でないことを検証する"""
        if value is not None and not value.strip():
            raise ValueError("must not be empty")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        """旅行状態の妥当性を検証する"""
        if value is None:
            return None
        if not value.strip():
            raise ValueError("must not be empty")
        try:
            PlanStatus(value)
        except ValueError as exc:
            raise ValueError("invalid status") from exc
        return value
```

### レスポンススキーマ

```python
class TravelPlanListResponse(BaseModel):
    """旅行計画一覧レスポンス"""
    id: str
    title: str
    destination: str
    status: str
    guide_generation_status: str = Field(..., alias="guideGenerationStatus")
    reflection_generation_status: str = Field(..., alias="reflectionGenerationStatus")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_dto(cls, dto: TravelPlanDTO) -> "TravelPlanListResponse":
        """DTOから一覧レスポンスを生成する"""
        return cls(
            id=dto.id,
            title=dto.title,
            destination=dto.destination,
            status=dto.status,
            guideGenerationStatus=dto.guide_generation_status,
            reflectionGenerationStatus=dto.reflection_generation_status,
        )


class TravelPlanResponse(BaseModel):
    """旅行計画レスポンス"""
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

    model_config = {"populate_by_name": True}
```

### レスポンス例

**旅行計画一覧**:
```json
[
  {
    "id": "plan_123",
    "title": "京都歴史探訪",
    "destination": "京都",
    "status": "planning",
    "guideGenerationStatus": "pending",
    "reflectionGenerationStatus": "pending"
  }
]
```

**個別旅行計画**:
```json
{
  "id": "plan_123",
  "userId": "user_456",
  "title": "京都歴史探訪",
  "destination": "京都",
  "spots": [
    {
      "id": "spot_1",
      "name": "金閣寺",
      "description": "金色に輝く美しい寺院",
      "userNotes": "朝早く訪問したい"
    }
  ],
  "status": "planning",
  "guideGenerationStatus": "completed",
  "reflectionGenerationStatus": "pending",
  "createdAt": "2025-01-29T10:00:00Z",
  "updatedAt": "2025-01-30T10:00:00Z",
  "guide": {
    "id": "guide_789",
    "title": "京都の歴史ガイド",
    "content": "...",
    "generatedAt": "2025-01-29T11:00:00Z"
  },
  "reflection": null,
  "pamphlet": null
}
```

### 設計のポイント

1. **リソース指向設計**: `/travel-plans`、`/travel-plans/{plan_id}`
2. **適切なHTTPメソッド**: POST（作成）、GET（取得）、PUT（更新）、DELETE（削除）
3. **適切なステータスコード**: 201（作成）、200（取得・更新）、204（削除）、404（Not Found）、400（Bad Request）
4. **構造化されたエラーレスポンス**: HTTPExceptionでdetailを返す
5. **Pydanticバリデーション**: リクエストスキーマでバリデーション
6. **関連リソースの埋め込み**: `guide`、`reflection`をレスポンスに含める
7. **一貫した命名規則**: キャメルケースでフィールド名を統一（`userId`、`createdAt`）
8. **ドキュメント化**: 詳細なdocstringとsummary

## まとめ

ドメイン別API設計のポイント:

1. **ユーザー管理**: シングルトンリソース（profile、settings）、アクション（password/reset）
2. **Eコマース**: ネストされたリソース（items、payment、shipment）、ステータス管理
3. **ブログ/CMS**: 多対多リレーション（tags）、全文検索、公開ステータス
4. **旅行計画**: 関連リソースの埋め込み、ステータス管理、Pydanticバリデーション

これらの例を参考に、ドメインの特性に応じたAPI設計を行うことができる。
