# Implementation Plan: Historical Travel Agent

## Overview

歴史学習特化型旅行AIエージェントシステムの実装計画。フロントエンドはTypeScript/Next.js 16、バックエンドはPython/FastAPIを使用し、Domain-Driven Design (DDD)アーキテクチャで構築します。

## Tasks

- [ ] 1. プロジェクト構造とコア設定の初期化
  - プロジェクトディレクトリ構造を作成
  - フロントエンド（Next.js 16 + TypeScript）とバックエンド（Python/FastAPI）の基本設定
  - 開発環境用Docker Compose設定（PostgreSQL, Redis）
  - 環境変数テンプレート（.env.example）の作成
  - _Requirements: 5.1, 5.2, 5.3_

- [ ] 2. バックエンド基盤の実装
  - [ ] 2.1 FastAPI基本設定とDDD構造の実装
    - FastAPIアプリケーションのエントリーポイント作成
    - Domain/Application/Infrastructure/Interfacesの4層構造を実装
    - 基本的なCORS設定とミドルウェア
    - _Requirements: 5.1, 5.3_

  - [ ] 2.2 データベース設定とモデル定義
    - SQLAlchemyモデルの定義（TravelPlan, TravelGuide, Reflection）
    - データベース接続とマイグレーション設定
    - _Requirements: 1.1, 3.1_

  - [ ] 2.3 基本的なREST APIエンドポイントの実装
    - /api/v1/travel-plans の基本CRUD操作
    - Pydanticスキーマの定義
    - _Requirements: 1.1, 3.1_

- [ ] 3. ドメイン層の実装
  - [ ] 3.1 TravelPlan集約の実装
    - TravelPlan, TouristSpotエンティティの実装
    - Location, PlanStatus値オブジェクトの実装
    - ITravelPlanRepositoryインターフェースの定義
    - _Requirements: 1.1_

  - [ ] 3.2 TravelPlan集約のプロパティテスト
    - **Property 1: Travel information storage**
    - **Validates: Requirements 1.1**

  - [ ] 3.3 TravelGuide集約の実装
    - TravelGuideエンティティの実装
    - HistoricalEvent, SpotDetail, Checkpoint値オブジェクトの実装
    - TravelGuideComposerドメインサービスの実装
    - _Requirements: 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4_

  - [ ] 3.4 TravelGuide集約のプロパティテスト
    - **Property 3: Timeline generation**
    - **Property 4: Map generation with historical context**
    - **Property 5: Travel guide completeness**
    - **Validates: Requirements 1.3, 1.4, 1.5**

  - [ ] 3.5 振り返り集約の実装
    - Reflection, Photoエンティティの実装
    - ImageAnalysis, ReflectionPamphlet値オブジェクトの実装
    - ReflectionAnalyzerドメインサービスの実装
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 3.6 振り返り集約のプロパティテスト
    - **Property 10: Image analysis execution**
    - **Property 11: Information integration**
    - **Property 13: Reflection pamphlet generation**
    - **Validates: Requirements 3.1, 3.2, 3.4**

- [ ] 4. Checkpoint - ドメイン層の完成確認
  - すべてのテストが通ることを確認し、質問があればユーザーに確認する

- [ ] 5. AI統合とインフラ層の実装
  - [ ] 5.1 Gemini Client統合の実装
    - Vertex AI Gemini APIクライアントの実装
    - Function Calling機能の統合（Google Search, Maps, Vision）
    - マルチモーダル入力対応（テキスト + 画像）
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 5.2 AI統合のプロパティテスト
    - **Property 2: Web search execution**
    - **Property 6: Historical background summarization**
    - **Property 7: Historical highlights organization**
    - **Validates: Requirements 1.2, 2.1, 2.2**

  - [ ] 5.3 ストレージサービスの実装
    - ローカル開発用ファイルストレージ
    - Google Cloud Storage統合（本番用）
    - 画像アップロード処理
    - _Requirements: 5.4, 5.5_

  - [ ] 5.4 リポジトリ実装
    - TravelPlanRepository, TravelGuideRepository, ReflectionRepositoryの実装
    - PostgreSQLでの永続化処理
    - _Requirements: 1.1, 3.1_

- [ ] 6. アプリケーション層（ユースケース）の実装
  - [ ] 6.1 旅行計画関連ユースケースの実装
    - CreateTravelPlanUseCase
    - GetTravelPlanUseCase
    - _Requirements: 1.1_

  - [ ] 6.2 旅行ガイド生成ユースケースの実装
    - GenerateTravelGuideUseCase（歴史情報収集→年表生成→ガイド構成）
    - 外部AI/検索サービスとの統合
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4_

  - [ ] 6.3 ガイド生成のプロパティテスト
    - **Property 8: Checkpoint list inclusion**
    - **Property 9: Content integration completeness**
    - **Validates: Requirements 2.3, 2.4**

  - [ ] 6.4 振り返り関連ユースケースの実装
    - AnalyzePhotosUseCase
    - GenerateReflectionPamphletUseCase
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 6.5 振り返りのプロパティテスト
    - **Property 12: Information reorganization**
    - **Property 14: Reflection pamphlet completeness**
    - **Validates: Requirements 3.3, 3.5**

- [ ] 7. REST APIエンドポイントの完成
  - [ ] 7.1 旅行計画APIの実装
    - GET/POST /api/v1/travel-plans
    - GET/PUT /api/v1/travel-plans/{id}
    - _Requirements: 1.1_

  - [ ] 7.2 旅行ガイドAPIの実装
    - GET /api/v1/travel-guides/{id}
    - 旅行ガイド生成トリガー
    - _Requirements: 1.5, 2.4_

  - [ ] 7.3 振り返りAPIの実装
    - POST /api/v1/reflections
    - POST /api/v1/upload-images
    - _Requirements: 3.1, 3.4_

  - [ ] 7.4 API統合テスト
    - エンドツーエンドのAPI動作確認
    - エラーハンドリングのテスト
    - _Requirements: 1.1, 1.5, 3.1, 3.4_

- [ ] 8. Checkpoint - バックエンドの完成確認
  - すべてのテストが通ることを確認し、質問があればユーザーに確認する

- [ ] 9. フロントエンド基盤の実装
  - [ ] 9.1 Next.js 16プロジェクトの初期化
    - Next.js 16 App Router設定
    - TypeScript設定とBiome設定
    - 基本的なレイアウトとページ構造
    - _Requirements: 5.2_

  - [ ] 9.2 共通UIコンポーネントの実装
    - Button, Input, Modal等の基本コンポーネント
    - TypeScript型定義の作成
    - _Requirements: 1.1, 3.1_

  - [ ] 9.3 APIクライアントの実装
    - バックエンドAPIとの通信ライブラリ
    - エラーハンドリングとローディング状態管理
    - _Requirements: 5.3_

- [ ] 10. 旅行計画機能のフロントエンド実装
  - [ ] 10.1 旅行計画一覧・作成画面の実装
    - TravelList, TravelFormコンポーネント
    - 旅行先・観光スポット入力フォーム
    - _Requirements: 1.1_

  - [ ] 10.2 旅行ガイド表示機能の実装
    - TravelGuideコンポーネント
    - 年表、地図、見どころの表示
    - _Requirements: 1.5, 2.4_

  - [ ] 10.3 旅行計画UIのユニットテスト
    - コンポーネントの動作確認
    - フォーム入力バリデーション
    - _Requirements: 1.1, 1.5_

- [ ] 11. 写真アップロード・振り返り機能の実装
  - [ ] 11.1 画像アップロード機能の実装
    - ImageUploaderコンポーネント
    - ドラッグ&ドロップ対応
    - _Requirements: 3.1_

  - [ ] 11.2 振り返りフォームの実装
    - ReflectionFormコンポーネント
    - 感想・メモ入力機能
    - _Requirements: 3.2_

  - [ ] 11.3 振り返りパンフレット表示の実装
    - ReflectionPamphletコンポーネント
    - 旅行要約、スポット振り返り、次の旅提案の表示
    - _Requirements: 3.5_

  - [ ] 11.4 振り返り機能のユニットテスト
    - アップロード機能のテスト
    - パンフレット表示のテスト
    - _Requirements: 3.1, 3.5_

- [ ] 12. 統合とエンドツーエンドテスト
  - [ ] 12.1 フロントエンド・バックエンド統合
    - API通信の確認
    - CORS設定の調整
    - _Requirements: 5.3_

  - [ ] 12.2 エンドツーエンドテスト（Playwright）
    - 旅行前フェーズの完全なワークフロー
    - 旅行後フェーズの完全なワークフロー
    - _Requirements: 1.1, 1.5, 3.1, 3.5_

- [ ] 13. 最終チェックポイント - システム全体の動作確認
  - すべてのテストが通ることを確認し、質問があればユーザーに確認する

## Notes

- `*`マークの付いたタスクは削除され、すべてのタスクが必須として実装されます
- 各タスクは特定の要件への追跡可能性のために要件を参照
- チェックポイントで段階的な検証を確保
- プロパティテストは汎用的な正確性プロパティを検証
- ユニットテストは具体例とエッジケースを検証
- フロントエンドはTypeScript、バックエンドはPythonを使用
- ローカル開発環境ではuvicorn（バックエンド）とNext.js dev server（フロントエンド）を使用
