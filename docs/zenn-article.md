---
title: "歴史を「体験して学ぶ」旅行AIエージェント"
emoji: "🏯"
type: "tech"
topics: ["GoogleCloud", "Gemini", "NextJS", "FastAPI", "AI"]
published: false
---

## デモ動画

<!-- TODO: YouTube動画URLを追加 -->

## 解決する課題

歴史の学習には、こんな課題がありませんか？

- **暗記中心で興味を持ちにくい** — 年号や人名を覚えるだけでは、歴史の面白さが伝わりません
- **断片的な知識で、つながりが見えない** — 個々の事実は知っていても、時代や場所の文脈が実感できません
- **現地体験と学習が分断される** — 旅行先で歴史的な場所を訪れても、事前知識がなければ「見ただけ」で終わってしまいます

歴史を本当に理解するには、教科書の知識と実際の場所をつなげる体験が必要です。しかし、旅行前に目的地の歴史を調べ、現地で学び、帰宅後に振り返るという一連の流れを自分で組み立てるのは大変です。

## このアプリでできること

本アプリは、旅行を通じた歴史学習の全体験を一貫して支援するAIエージェントです。

<img src="./images/user-journey.svg" alt="ユーザージャーニー: 事前学習→現地体験→振り返り" width="400" />

**事前学習（旅行前）**: 目的地と訪れたいスポットを入力するだけで、AIが旅行ガイドを生成します。歴史年表、各スポットの歴史的背景、見どころ、チェックポイントを含み、Google Search groundingで正確な歴史情報を提供します。

**現地体験（旅行中）**: 生成されたガイドとGoogle Mapsを使って、歴史的文脈を理解しながらスポットを巡ります。チェックポイントに沿って観察することで、ただ見るだけでは気づかない歴史の痕跡を発見できます。

**振り返り（旅行後）**: 旅行で撮った写真と感想をアップロードすると、AIが旅行の振り返りパンフレットを生成します。写真の分析結果と感想を統合し、体験を記録として残します。

## 主な機能

<img src="./images/feature-flow.svg" alt="機能フロー: 旅行計画作成からパンフレット生成まで" width="700" />

### 旅行計画の作成

目的地と観光スポットを入力して、旅行計画を作成します。

<!-- TODO: 旅行計画作成画面のスクリーンショットを追加 -->

### AI旅行ガイドの生成

入力した情報をもとに、AIが以下を含む旅行ガイドを自動生成します。

- **歴史年表** — 目的地に関連する歴史的出来事を時系列で整理
- **スポット詳細** — 各観光スポットの歴史的背景と見どころ
- **チェックポイント** — 現地で確認すべきポイント

<!-- TODO: 旅行ガイド表示画面のスクリーンショットを追加 -->

### Google Maps連携

観光スポットの位置をGoogle Maps上にマーカーで表示します。Places APIによるスポット検索と、番号付きマーカーによる訪問順の可視化に対応しています。

<!-- TODO: Google Maps表示のスクリーンショットを追加 -->

### スポット画像の自動生成

各観光スポットのイメージ画像をAIが自動生成します。非同期ジョブキューで処理するため、ガイド生成完了後にバックグラウンドで画像が順次生成されます。

<!-- TODO: スポット画像表示のスクリーンショットを追加 -->

### 振り返りパンフレットの生成

旅行後に写真と感想をアップロードすると、AIが振り返りパンフレットを生成します。スポットごとの写真分析と感想を統合し、旅行の記録を一つのパンフレットにまとめます。

<!-- TODO: 振り返りパンフレット画面のスクリーンショットを追加 -->

## システムアーキテクチャ

<img src="./images/architecture.svg" alt="システムアーキテクチャ" width="600" />

Frontend（Next.js 16）とBackend（FastAPI）はそれぞれCloud Runにデプロイしています。BackendはVertex AI（gemini-3-preview）で旅行ガイドと振り返りパンフレットを生成し、スポット画像はgemini-2.5-flash-imageで生成します。データはCloud SQLに永続化し、画像はCloud Storageに保存します。スポット画像の生成はCloud Tasks経由で非同期に実行されます。

## 技術的な工夫

### エージェント構成

各機能はそれぞれ独立したエージェントとして実装しており、Google SearchやCloud Storageなどのツールを組み合わせて動作します。

**ガイド生成エージェント**: 旅行ガイドの生成を担当
<img src="./images/agent-guide.svg" alt="ガイド生成エージェント" width="500" />

**写真分析エージェント**: アップロード写真の分析を担当
<img src="./images/agent-photo.svg" alt="写真分析エージェント" width="300" />

**画像生成エージェント**: スポット画像の生成を担当
<img src="./images/agent-image.svg" alt="画像生成エージェント" width="400" />

**振り返り生成エージェント**: 振り返りパンフレットの生成を担当
<img src="./images/agent-reflection.svg" alt="振り返り生成エージェント" width="250" />

### 2段階のガイド生成

旅行ガイドの生成は、2つのステップに分けて実行しています。

1. **事実抽出（Step A）**: Google Search groundingを有効にして、目的地とスポットに関する歴史的事実を収集します。Web検索結果に基づく情報収集により、ハルシネーションを抑制します
2. **ガイド構築（Step B）**: 収集した事実をもとに、構造化出力（JSON Schema）でガイドを生成します。年表・スポット詳細・チェックポイントを型安全に出力させることで、データ品質を担保します

この2段階構成により、「情報の正確性」と「出力の構造化」を両立しています。

### Google Search groundingによるハルシネーション対策

Gemini APIのGoogle Search grounding機能を活用し、Web上の情報源に基づいた回答を生成します。生成結果にはgroundingメタデータ（情報源URL、検索クエリ）が付与されるため、情報の出典を追跡できます。

### 構造化出力（JSON Schema）による品質保証

Gemini APIの構造化出力機能を使い、Pydanticモデルで定義したJSON Schemaに沿った出力を強制しています。フィールドの制約（最小文字数、最小項目数など）をバリデーションで検証することで、出力品質を安定させています。

### 非同期ジョブキューによるスポット画像生成

スポット画像の生成は、ガイド生成とは独立した非同期ジョブとして実行しています。

- **ローカル開発**: DBベースのジョブキューと専用ワーカーで処理
- **本番環境**: Cloud Tasksでタスクをディスパッチし、専用のCloud Runサービスで処理

PostgreSQLの`FOR UPDATE SKIP LOCKED`による排他制御で、複数ワーカーの並列実行にも対応しています。画像生成の失敗がガイド生成の成功に影響しない設計としています。

### DDD + クリーンアーキテクチャ

バックエンドはDDD（Domain-Driven Design）とクリーンアーキテクチャに基づいて設計しています。

- **Domain層**: ビジネスロジックとエンティティ（TravelPlan、TravelGuide、Reflection）
- **Application層**: ユースケースとポート（IAIService、IImageGenerationService）
- **Infrastructure層**: 外部サービスとの接続（Gemini、Cloud Storage、Cloud Tasks）
- **Interface層**: APIエンドポイントとスキーマ

依存性の方向を内側（Domain）に向けることで、AIサービスやストレージの差し替えが容易な構造にしています。

## 使用技術

| カテゴリ | 技術 |
|---------|------|
| Frontend | Next.js 16 (App Router), React 19, TypeScript |
| Backend | FastAPI, Python 3.12, Pydantic |
| AI | Vertex AI (gemini-3-preview, gemini-2.5-flash-image) |
| Database | Cloud SQL (PostgreSQL), SQLAlchemy, Alembic |
| Storage | Cloud Storage |
| Queue | Cloud Tasks |
| Infrastructure | Cloud Run, Secret Manager, Artifact Registry |
| Map | Google Maps JavaScript API, Places API |
| Testing | pytest, Vitest, Playwright |
| CI/CD | GitHub Actions |

## 今後の展望

- **ユーザー認証**: 個人の旅行履歴を蓄積し、過去の旅行との関連づけを可能にする
- **多言語対応**: 海外の歴史スポットにも対応し、訪日外国人の利用もサポートする
- **旅行シェアリング**: 生成したガイドやパンフレットを他のユーザーと共有できるようにする

## リポジトリ

<!-- TODO: GitHubリポジトリURLを追加 -->

## まとめ

本アプリは、歴史学習と旅行体験を結びつけるAIエージェントです。旅行前の事前学習、旅行中の現地ガイド、旅行後の振り返りという3つのフェーズを一貫して支援することで、歴史を「体験して学ぶ」導線を提供します。

Vertex AI（gemini-3-preview）のGoogle Search groundingと構造化出力を活用し、正確で構造化された歴史情報を生成しています。Cloud TasksとCloud Runによる非同期処理基盤と、DDD + クリーンアーキテクチャによる拡張性の高い設計により、今後の機能追加にも柔軟に対応できる構成としています。
