# 第４回 AI Hackathon with Google Cloud 提出作品開発リポジトリ

## 概要

このリポジトリは、[第4回 Agentic AI Hackathon with Google Cloud](https://zenn.dev/hackathons/google-cloud-japan-ai-hackathon-vol4) に提出するプロジェクトの開発リポジトリです。

## ハッカソンについて

### テーマ
「進化するAIと共に。君だけの「エージェント」を創り出そう。」

自律的に動作するAIエージェント開発を中心テーマとした、第4回目のGoogle Cloud AI Hackathonです。最新の「Gemini 3」モデルとAntiGravityなどのツールを活用した次世代AIコーディングが体験できます。

### スケジュール
- **応募期間**: 2025年12月10日～2026年2月15日
- **1次審査**: 2月16日～23日
- **2次審査**: 2月24日～3月2日
- **最終イベント**: 2026年3月19日（Google Cloud Agentic AI Summit '26 Spring）

### 賞金
- **最優秀賞**: 50万円（1件）
- **優秀賞**: 25万円×3件
- **奨励賞**: 10万円×5件

### 必須要件
プロジェクトはGoogle Cloudの実行プロダクト（App Engine、Cloud Run、GKE等）とAI技術（Vertex AI、Gemini API等）の両方を組み合わせて利用する必要があります。

### 審査基準

#### 課題の新規性
多くの人が抱えていて、いまだに解決策が与えられていない課題を発見したプロジェクトを評価します。

#### 解決策の有効性
提案されたソリューションがその中心となる課題に効果的に対処し、解決しているかを評価します。

#### 実装品質と拡張性
開発者がアイデアをどの程度実現し、必要なツールを活用し、拡張性があり、運用しやすく、費用対効果の高いソリューションを作成できたかを評価します。

---

## プロジェクト概要

### プロジェクト名
<!-- プロジェクト名を記載 -->

**_History Learning Agent_**

### 一行説明
<!-- プロジェクトを一言で説明 -->

歴史学習のサポートおよび自分専用の歴史体験記作成エージェント

## 解決する課題
<!-- 現在どのような問題があり、誰がどのように困っているのかを具体的に記載 -->

- 歴史教育の難解さ
  - 教科書の暗記が中心
  - 歴史に興味を持ちにくい
  - 現代とかけ離れていてイメージが湧かない
- 知識の断片化
  - 年号や事実の言葉による説明だけで臨場感がない
  - 教科書には必要最低限のことしか書かれない

### 背景
<!-- なぜこの課題に取り組むのか、社会的背景や個人的な動機を記載 -->

- 歴史の結びつきを考えるきっかけになる
- 事前学習および実体験、振り返りは記憶定着率が高い
- 楽しい教育学習の需要は拡大中

### ターゲットユーザー
<!-- このプロジェクトが解決を目指す対象者・ユーザー層を記載 -->

- 学生
- 教育者
- 歴史好き
- 観光者

## ソリューション（解決策の有効性）

### 提案する解決策
<!-- AIエージェントを使ってどのように課題を解決するのかを記載 -->

事前、道中の情報収集をAIエージェントでサポートし、実体験を楽しく振り返り記憶の定着に貢献するような自分だけのコンテンツを自律的に提供するエージェントを作成し解決を試みる

### 主な機能

- 行先への事前学習
  - その土地の名所と説明
  - その土地の年表
- 道中の注釈サポート
  - 現在地からスポットの提案
- 行った先の事後学習
  - 自分専用のパンフレット

### 期待される効果
<!-- このソリューションによって得られる効果・メリットを記載 -->

- 歴史に対してドキドキワクワクする
- 歴史的体験を記憶だけじゃなく物理的な思い出も残る

## アーキテクチャ（実装品質と拡張性）

### システム構成
```
[アーキテクチャ図やシステム構成図を記載]
```

### 技術スタック

<!-- TODO 設計書がマージされたら追記する -->

### 前提条件
- **開発環境**:
  - [just](https://github.com/casey/just) - タスクランナー（`brew install just`でインストール）
  - [uv](https://github.com/astral-sh/uv) - Pythonパッケージ管理（`brew install uv`でインストール）
  - [pnpm](https://pnpm.io/) - Node.jsパッケージ管理（`brew install pnpm`でインストール）
  - Python 3.12以上
  - Node.js 18以上
- **必要なアカウント**:
  - Google Cloudアカウント
  - Vertex AI APIの有効化

### セットアップ手順
```bash
# リポジトリのクローン
git clone [repository-url]
cd <repository-directory>

# 依存関係のインストール（バックエンド + フロントエンド）
just install-all

# Google Cloud認証（Application Default Credentials）
gcloud auth application-default login

# 環境変数の設定
# バックエンドの環境変数
cp backend/.env.example backend/.env
# backend/.envファイルを編集して必要な環境変数を設定

# フロントエンドの環境変数（必要に応じて）
cp frontend/.env.local.example frontend/.env.local
# frontend/.env.localファイルを編集して必要な環境変数を設定
```

### ローカル開発

#### 開発サーバーの起動

```bash
# バックエンド + フロントエンド同時起動
just dev-all

# または個別に起動
just dev-backend   # バックエンドのみ（http://localhost:8000）
just dev-frontend  # フロントエンドのみ（http://localhost:3000）
```

#### よく使うタスク

```bash
# コマンド一覧を表示
just

# テスト実行
just test-all              # 全テスト実行
just test-backend          # バックエンドのみ
just test-frontend         # フロントエンドのみ
just test-backend-cov      # カバレッジ付き（バックエンド）

# コード品質チェック
just check-quality         # 全品質チェック（Lint + Format + 型チェック）
just lint-all              # Lint実行
just format-all            # フォーマット実行
just typecheck-all         # 型チェック実行

# ビルド
just build-frontend        # フロントエンドのプロダクションビルド

# クリーンアップ
just clean-all             # キャッシュとビルド成果物を削除
```

利用可能な全コマンドは `just --list` で確認できます。

### CI/CD（GitHub Actions）

プロジェクトでは段階的な品質チェックパイプラインを採用しています。

#### パイプライン概要

```
PR作成/更新 → Stage 1: Lint Check → Stage 2: Code Quality Check → ✅ Ready for Review
```

- **Stage 1**: コードスタイル・型チェック (`just check-quality`)
- **Stage 2**: テスト実行・ビルド検証 (`just test-backend-cov`, `just test-frontend`, `just build-frontend`)

各ステージは前のステージが成功した場合のみ実行され、失敗時はパイプラインが終了します。

#### ローカルでの事前チェック

CI/CDと全く同じコマンドでローカルチェックが可能：

```bash
just install-all      # 依存関係インストール
just check-quality    # Stage 1相当
just test-backend-cov # Stage 2相当（バックエンドテスト）
just test-frontend    # Stage 2相当（フロントエンドテスト）
just build-frontend   # Stage 2相当（ビルド）
```

#### 詳細情報

CI/CDワークフローの詳細な設計・仕様・トラブルシューティングについては、以下のドキュメントを参照してください：

📖 **[CI/CDワークフロー設計書](docs/actions/ci-workflow-design.md)**

### デプロイ
```bash
# Google Cloudへのデプロイ
[デプロイコマンドを記載]
```

## デモ

### デプロイURL
[デプロイされたアプリケーションのURLを記載]

### スクリーンショット
[アプリケーションのスクリーンショットを追加]

### デモ動画
[デモ動画のリンクまたは埋め込みを追加]

## 提出物

ハッカソンへの提出には以下が必要です：

1. **GitHubリポジトリURL**（公開）- このリポジトリ
2. **デプロイURL** - [URLを記載予定]
3. **Zennの記事** - [記事URLを記載予定]
   - アーキテクチャ図
   - デモ動画（3分程度）

## ライセンス

[ライセンスを記載予定]
