# フロントエンド画面設計書

## 概要

歴史学習特化型旅行AIエージェントシステムのフロントエンド画面設計。Next.js 16 App Routerを使用し、旅行前の事前学習から旅行後の振り返りまでのユーザージャーニーをサポートする画面構成。

## 関連ドキュメント

- [システム設計書（Kiro）](../../.kiro/specs/historical-travel-agent/design.md) - アーキテクチャ、データモデル、API設計
- [UIコンポーネント一覧](./ui-components.md) - 共通UIコンポーネントの詳細

## 画面構成

### 1. メイン画面・ナビゲーション

#### ホーム画面 (`/`)
- **目的**: システム概要とメイン機能への導線
- **主要機能**:
  - システムの説明とメリット紹介
  - 旅行前フェーズ（事前学習）への導線
  - 旅行後フェーズ（振り返り）への導線
  - 使い方ガイド
- **コンポーネント**: `app/page.tsx`

### 2. 旅行前フェーズの画面

#### 旅行一覧画面 (`/travel`)
- **目的**: 作成済み旅行計画の管理
- **主要機能**:
  - 旅行計画一覧の表示
  - 新規旅行作成ボタン
  - 各旅行の状態表示（planning/completed）
  - 旅行の編集・削除機能
- **コンポーネント**: 
  - `app/travel/page.tsx`
  - `components/travel/TravelList.tsx`

#### 新規旅行作成画面 (`/travel/new`)
- **目的**: 新しい旅行計画の作成
- **主要機能**:
  - 旅行タイトル入力
  - 旅行先（目的地）入力
  - 観光スポット選択・追加
  - 旅行ガイド生成トリガー
- **コンポーネント**:
  - `app/travel/new/page.tsx`
  - `components/travel/TravelForm.tsx`
  - `components/travel/SpotSelector.tsx`

#### 旅行ガイド表示画面 (`/travel/[id]`)
- **目的**: AI生成された旅行ガイドの表示
- **主要機能**:
  - 旅行概要の表示
  - 歴史年表（Timeline）の表示
  - 各スポットの詳細情報
    - 歴史的背景
    - 見どころ
    - チェックポイント
  - 旅行完了マーク機能
- **コンポーネント**:
  - `app/travel/[id]/page.tsx`
  - `components/display/TravelGuide.tsx`
  - `components/display/Timeline.tsx`

### 3. 旅行後フェーズの画面

#### 振り返り一覧画面 (`/reflection`)
- **目的**: 完了した旅行の振り返り管理
- **主要機能**:
  - 完了ステータス（status='completed'）の旅行一覧表示
  - 振り返り作成状況の表示
    - 未作成：新規振り返り作成への導線
    - 作成済み：振り返りパンフレットの閲覧のみ（編集不可）
  - 既存振り返りパンフレットの閲覧
- **コンポーネント**:
  - `app/reflection/page.tsx`
  - `components/reflection/ReflectionList.tsx`

#### 振り返り作成画面 (`/reflection/[id]`)
- **目的**: 旅行後のスポット別写真と感想の収集
- **アクセス制御**: 振り返り未作成の旅行のみアクセス可能（作成済みは閲覧専用画面へリダイレクト）
- **主要機能**:
  - **計画スポット表示**: 旅行計画に含まれていたスポットの一覧表示
  - **スポット別画像アップロード**: 各スポットに対する複数画像のアップロード（ドラッグ&ドロップ対応）
  - **スポット別感想入力**: 各スポットに対する感想入力（任意）
  - **スポット追加機能**: 
    - 計画になかった観光スポットの追加
    - 観光スポット名の入力（必須）
    - 追加スポットへの画像アップロード・感想入力
  - **全体感想入力**: 旅行全体に対する感想入力（任意）
  - **旅行前情報との比較**: 旅行ガイドとの比較表示
  - **振り返りパンフレット生成**: AI処理トリガー
- **データ仕様**:
  - 追加されたスポットは振り返り専用データとして保存
  - 元の旅行計画には影響しない
  - 一度作成完了した振り返りは編集不可
- **コンポーネント**:
  - `app/reflection/[id]/page.tsx`
  - `components/reflection/SpotReflectionForm.tsx`
  - `components/reflection/SpotAdder.tsx`
  - `components/upload/ImageUploader.tsx`

#### 振り返り閲覧画面 (`/reflection/[id]/view`)
- **目的**: 作成済み振り返りパンフレットの閲覧
- **アクセス制御**: 振り返り作成済みの旅行のみアクセス可能
- **主要機能**:
  - 生成された振り返りパンフレットの表示
  - 編集機能なし（閲覧専用）
- **コンポーネント**:
  - `app/reflection/[id]/view/page.tsx`
  - `components/reflection/ReflectionViewer.tsx`

### 4. 共通機能画面

#### ローディング画面
- **目的**: AI生成処理中の進行状況表示
- **主要機能**:
  - 処理進行状況の表示
  - 処理時間の目安表示
  - キャンセル機能（可能な場合）
  - ガイド/振り返り生成ステータスに応じた表示切替
- **コンポーネント**: `components/ui/LoadingSpinner.tsx`

#### エラー画面
- **目的**: エラー発生時のユーザー対応
- **主要機能**:
  - エラー内容の分かりやすい説明
  - 再試行ボタン
  - サポート連絡先
- **コンポーネント**: `components/ui/ErrorBoundary.tsx`

## コンポーネント構成

```
frontend/src/
├── app/                          # Next.js 16 App Router
│   ├── layout.tsx               # 全体レイアウト
│   ├── page.tsx                 # ホーム画面
│   ├── travel/
│   │   ├── page.tsx            # 旅行一覧画面
│   │   ├── new/
│   │   │   └── page.tsx        # 新規旅行作成画面
│   │   └── [id]/
│   │       └── page.tsx        # 旅行ガイド表示画面
│   ├── reflection/
│   │   ├── page.tsx            # 振り返り一覧画面
│   │   └── [id]/
│   │       ├── page.tsx        # 振り返り作成画面
│   │       └── view/
│   │           └── page.tsx    # 振り返り閲覧画面
│   └── api/                     # Next.js API Routes (プロキシ用)
│       └── proxy/
├── components/
│   ├── ui/                      # 共通UIコンポーネント
│   │   ├── Button.tsx
│   │   ├── TextField.tsx
│   │   ├── Modal.tsx
│   │   ├── LoadingSpinner.tsx
│   │   └── ErrorBoundary.tsx
│   ├── travel/                  # 旅行計画関連
│   │   ├── TravelList.tsx
│   │   ├── TravelForm.tsx
│   │   └── SpotSelector.tsx
│   ├── upload/                  # アップロード関連
│   │   └── ImageUploader.tsx
│   ├── display/                 # 表示関連
│   │   ├── TravelGuide.tsx
│   │   └── Timeline.tsx
│   └── reflection/              # 振り返り関連
│       ├── ReflectionList.tsx
│       ├── SpotReflectionForm.tsx
│       ├── SpotAdder.tsx
│       └── ReflectionViewer.tsx
├── lib/
│   ├── api.ts                   # APIクライアント
│   ├── utils.ts                 # ユーティリティ関数
│   └── validations.ts           # バリデーション
├── types/
│   ├── travel.ts                # 旅行関連の型定義
│   ├── guide.ts                 # ガイド関連の型定義
│   └── reflection.ts            # 振り返り関連の型定義
├── hooks/
│   ├── useTravel.ts             # 旅行関連のカスタムフック
│   └── useUpload.ts             # アップロード関連のカスタムフック
└── styles/
    └── globals.css              # グローバルスタイル
```

## ユーザージャーニー

### 旅行前フェーズ
1. ホーム画面でシステム概要を確認
2. 旅行一覧画面で既存旅行を確認または新規作成を選択
3. 新規旅行作成画面で旅行先と観光スポットを入力
4. AI処理によるガイド生成（ローディング画面）
5. 旅行ガイド表示画面で生成されたガイドを確認

### 旅行後フェーズ
1. 振り返り一覧画面で完了ステータスの旅行から振り返り対象を選択
2. 振り返り作成状況に応じて画面が分岐：
   - **未作成の場合**: 振り返り作成画面で写真・感想を入力し、AI処理による振り返りパンフレット生成
   - **作成済みの場合**: 振り返り閲覧画面で生成済みパンフレットを閲覧（編集不可）

## 技術仕様

- **フレームワーク**: Next.js 16 (App Router)
- **言語**: TypeScript
- **スタイリング**: CSS Modules / Tailwind CSS
- **状態管理**: React hooks + Context API
- **フォーム管理**: React Hook Form
- **画像アップロード**: ドラッグ&ドロップ対応
- **レスポンシブ対応**: モバイルファースト
- **アクセシビリティ**: WCAG 2.1 AA準拠

## 要件との対応

この画面設計は以下の要件を満たします：

- **Requirement 1**: 旅行前情報収集 → 旅行作成・ガイド表示画面
- **Requirement 2**: 歴史情報コンテンツ生成 → ガイド表示画面の詳細表示
- **Requirement 3**: 旅行後振り返り支援 → 写真アップロード・パンフレット表示画面
- **Requirement 4**: AI技術統合 → 各画面でのAI生成機能
- **Requirement 5**: ローカル開発環境 → Next.js 16開発サーバー対応
