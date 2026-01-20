# コードレビューガイドライン

コードレビューに関して、以下のガイダンスに従ってください

## 制約条件

- レビューコメントは日本語で記入してください
- レビューコメントは具体的かつ建設的にしてください
- コードの可読性、保守性、パフォーマンスに焦点を当ててください

## レビュー優先度

1. バグやセキュリティの問題
2. NextJsとTypescript,FastAPIのベストプラクティスへの準拠
3. コードの可読性と保守性
4. パフォーマンスの最適化

## フロントエンド

- UI表示する文言はリテラルではなく、frontend/src/constants/*.tsに定義されていること
- コンポーネントは再利用可能な形で設計されていること
- スタイルはTailwindCSSを用いて一貫性があること

## バックエンド

- エンドポイントはRESTfulな設計になっていること
- ドメイン駆動設計になっていること

## NextJs

- AppRoutingを採用していること
- use client/server componentの適切な使い分け

## TypeScript

- 型定義が適切に行われていること
- any型の使用を避けること
- 非同期処理が適切に扱われていること

---

# プロジェクト構成

## プロジェクト概要

歴史学習特化型旅行AIエージェントシステム（Historical Travel Agent）は、Geminiの強力なマルチモーダル機能とツール機能を活用して、旅行者に歴史的コンテキストを提供するシステムです。

システムは以下の2つの主要フェーズで動作します：
1. **旅行前フェーズ**: ユーザーの旅行計画に基づいて歴史情報を収集・整理し、包括的な旅行ガイドを生成
2. **旅行後フェーズ**: ユーザーの写真や感想を分析し、学習体験を振り返るパンフレットを生成

## 技術スタック

### フロントエンド
- **フレームワーク**: React + Next.js 16 (App Router)
- **言語**: TypeScript
- **パッケージマネージャー**: pnpm
- **Linter/Formatter**: Biome
- **スタイリング**: Tailwind CSS
- **ホスティング**: Firebase Hosting
- **テスト**: Vitest, Playwright Test Agent

### バックエンド
- **フレームワーク**: Python + FastAPI
- **アーキテクチャ**: Domain-Driven Design (DDD)
- **パッケージマネージャー**: uv
- **Linter/Formatter**: Ruff
- **型チェック**: Pyright
- **データベース**: PostgreSQL
- **キャッシュ**: Redis
- **ホスティング**: Google Cloud Run
- **テスト**: pytest, Hypothesis (Property-based testing)

### AI/ML
- **AI サービス**: Vertex AI Gemini
- **ビルトインツール**: Google Search, Google Maps, Image Analysis
- **ストレージ**: Google Cloud Storage

## ディレクトリ構成

### フロントエンド構造

```
frontend/                    # React/Next.js 16/TypeScript フロントエンド
├── package.json
├── pnpm-lock.yaml
├── next.config.js
├── tsconfig.json
├── biome.json              # Biome設定（Linter/Formatter）
├── public/
│   ├── favicon.ico
│   └── images/
├── src/
│   ├── app/                # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx        # トップページ
│   │   ├── travel/         # 旅行計画関連ページ
│   │   │   ├── page.tsx    # 旅行一覧
│   │   │   ├── [id]/
│   │   │   │   └── page.tsx    # 旅行詳細
│   │   │   └── new/
│   │   │       └── page.tsx    # 新規旅行作成
│   │   ├── reflection/     # 振り返り関連ページ
│   │   │   ├── page.tsx
│   │   │   └── [id]/
│   │   │       └── page.tsx
│   │   └── api/            # Next.js API Routes (プロキシ用)
│   │       └── proxy/
│   ├── components/
│   │   ├── ui/             # 共通UIコンポーネント
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   ├── travel/         # 旅行関連コンポーネント
│   │   │   ├── TravelList.tsx
│   │   │   ├── TravelForm.tsx
│   │   │   └── SpotSelector.tsx
│   │   ├── upload/         # アップロード関連コンポーネント
│   │   │   ├── ImageUploader.tsx
│   │   │   └── ReflectionForm.tsx
│   │   └── display/        # 表示用コンポーネント
│   │       ├── TravelGuide.tsx
│   │       └── ReflectionPamphlet.tsx
│   ├── constants/          # 定数定義（UI表示文言など）
│   │   └── *.ts
│   ├── lib/                # ユーティリティ
│   │   ├── api.ts          # API通信
│   │   ├── utils.ts
│   │   └── validations.ts
│   ├── types/              # TypeScript型定義
│   │   ├── travel.ts
│   │   ├── guide.ts
│   │   └── reflection.ts
│   ├── hooks/              # カスタムフック
│   │   ├── useTravel.ts
│   │   └── useUpload.ts
│   └── styles/
│       └── globals.css
└── tests/
    ├── __tests__/
    │   ├── components/
    │   └── pages/
    ├── integration/
    └── e2e/                # Playwright Test Agent
```

### バックエンド構造（DDD アーキテクチャ）

```
backend/                    # Python/FastAPI バックエンド (DDD構造)
├── pyproject.toml          # uv設定
├── uv.lock
├── ruff.toml               # Ruff設定（Linter/Formatter）
├── pyrightconfig.json      # Pyright設定（型チェック）
├── .env.local              # ローカル環境変数
├── main.py                 # FastAPI エントリーポイント
├── app/
│   ├── domain/             # ドメイン層（ビジネスロジックの中核）
│   │   ├── travel_plan/    # TravelPlan集約
│   │   │   ├── entity.py           # TravelPlan, TouristSpot エンティティ
│   │   │   ├── value_objects.py    # Location, PlanStatus 値オブジェクト
│   │   │   ├── repository.py       # ITravelPlanRepository インターフェース
│   │   │   └── exceptions.py
│   │   ├── travel_guide/   # TravelGuide集約
│   │   │   ├── entity.py           # TravelGuide エンティティ
│   │   │   ├── value_objects.py    # HistoricalEvent, SpotDetail, Checkpoint
│   │   │   ├── repository.py       # ITravelGuideRepository インターフェース
│   │   │   ├── services.py         # TravelGuideComposer ドメインサービス
│   │   │   └── exceptions.py
│   │   ├── reflection/     # 振り返り集約
│   │   │   ├── entity.py           # Reflection, Photo エンティティ
│   │   │   ├── value_objects.py    # ImageAnalysis, ReflectionPamphlet
│   │   │   ├── repository.py       # IReflectionRepository インターフェース
│   │   │   ├── services.py         # ReflectionAnalyzer ドメインサービス
│   │   │   └── exceptions.py
│   │   └── shared/         # 共通ドメイン要素
│   │       ├── entity.py           # 基底Entity クラス
│   │       ├── value_object.py     # 基底ValueObject クラス
│   │       └── events.py           # ドメインイベント
│   │
│   ├── application/        # アプリケーション層（ユースケース）
│   │   ├── use_cases/
│   │   │   ├── create_travel_plan.py       # 旅行計画作成
│   │   │   ├── generate_travel_guide.py    # 旅行ガイド生成
│   │   │   ├── analyze_photos.py           # 写真分析
│   │   │   ├── generate_reflection.py      # 振り返り生成
│   │   │   └── get_travel_plan.py          # 旅行計画取得
│   │   ├── dto/            # データ転送オブジェクト
│   │   │   ├── travel_plan_dto.py
│   │   │   ├── travel_guide_dto.py
│   │   │   └── reflection_dto.py
│   │   └── ports/          # アプリケーション層のインターフェース
│   │       ├── ai_service.py               # IAIService インターフェース
│   │       ├── search_service.py           # ISearchService インターフェース
│   │       └── storage_service.py          # IStorageService インターフェース
│   │
│   ├── infrastructure/     # インフラ層（外部システム連携）
│   │   ├── repositories/   # リポジトリ実装
│   │   │   ├── travel_plan_repository.py
│   │   │   ├── travel_guide_repository.py
│   │   │   └── reflection_repository.py
│   │   ├── ai/             # AI統合
│   │   │   ├── gemini_client.py            # Gemini統合
│   │   │   └── adapters.py                 # AIサービスアダプタ
│   │   ├── search/         # 検索統合
│   │   │   └── google_search_client.py
│   │   ├── maps/           # 地図統合
│   │   │   └── google_maps_client.py
│   │   ├── storage/        # ストレージ
│   │   │   ├── local_storage.py            # ローカル開発用
│   │   │   └── cloud_storage.py            # 本番用
│   │   └── persistence/    # データ永続化
│   │       ├── models.py                   # SQLAlchemyモデル
│   │       └── database.py                 # DB接続
│   │
│   └── interfaces/         # インターフェース層（API）
│       ├── api/            # REST API
│       │   ├── v1/
│       │   │   ├── travel_plans.py
│       │   │   ├── travel_guides.py
│       │   │   ├── reflections.py
│       │   │   └── uploads.py
│       │   └── dependencies.py
│       ├── schemas/        # Pydanticスキーマ（リクエスト/レスポンス）
│       │   ├── travel_plan.py
│       │   ├── travel_guide.py
│       │   └── reflection.py
│       └── middleware/
│           ├── cors.py
│           └── error_handler.py
│
├── config/                 # 設定
│   ├── settings.py
│   └── dependencies.py
│
├── tests/                  # pytest テスト
│   ├── conftest.py
│   ├── unit/
│   │   ├── domain/                 # ドメインロジックのテスト
│   │   ├── application/            # ユースケースのテスト
│   │   └── infrastructure/         # インフラのテスト
│   ├── integration/                # 統合テスト
│   │   ├── test_api/
│   │   └── test_use_cases/
│   └── property/                   # Property-based tests
│       ├── test_travel_properties.py
│       └── test_content_properties.py
├── uploads/                # ローカル開発用アップロードディレクトリ
└── logs/                   # ログファイル
```

## API エンドポイント

### 主要エンドポイント (v1 API)

```
GET  /api/v1/travel-plans           # 旅行一覧取得
POST /api/v1/travel-plans           # 旅行計画作成
GET  /api/v1/travel-plans/{id}      # 旅行計画取得
PUT  /api/v1/travel-plans/{id}      # 旅行計画更新
GET  /api/v1/travel-guides/{id}     # 旅行ガイド取得
POST /api/v1/reflections            # 振り返り作成
POST /api/v1/upload-images          # 画像アップロード
```

## DDD設計の特徴

### 4層アーキテクチャ
1. **ドメイン層**: ビジネスロジックの中核（エンティティ、値オブジェクト、ドメインサービス）
2. **アプリケーション層**: ユースケースの実装とドメイン層のオーケストレーション
3. **インフラ層**: 外部システムとの連携（データベース、AI API、ストレージ）
4. **インターフェース層**: REST APIとスキーマ定義

### 主要な集約
- **TravelPlan集約**: 旅行計画の管理
- **TravelGuide集約**: 歴史情報を含む旅行ガイドの生成
- **振り返り集約**: 旅行後の写真分析と振り返り生成

### 依存性逆転の原則
ドメイン層がインターフェースを定義し、インフラ層が実装することで、ビジネスロジックを外部依存から分離しています。

## 参考資料

詳細な設計ドキュメント: `.kiro/specs/historical-travel-agent/design.md`