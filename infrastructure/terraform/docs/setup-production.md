# 本番環境セットアップ手順書

本ドキュメントは、本番環境のインフラストラクチャを構築するための詳細な手順を記載しています。

## 目次

1. [前提条件](#前提条件)
2. [本番用GCPプロジェクトの作成](#本番用gcpプロジェクトの作成)
3. [必要なAPIの有効化](#必要なapiの有効化)
4. [Terraformステートバケットの作成](#terraformステートバケットの作成)
5. [Terraform初期化](#terraform初期化)
6. [本番環境ワークスペースの作成](#本番環境ワークスペースの作成)
7. [本番用変数ファイルの作成](#本番用変数ファイルの作成)
8. [バックエンドDockerイメージのビルド＆プッシュ](#バックエンドdockerイメージのビルドプッシュ)
9. [フロントエンドDockerイメージのビルド＆プッシュ](#フロントエンドdockerイメージのビルドプッシュ)
10. [インフラストラクチャのデプロイ](#インフラストラクチャのデプロイ)
11. [データベースマイグレーションの実行](#データベースマイグレーションの実行)
12. [動作確認](#動作確認)
13. [トラブルシューティング](#トラブルシューティング)

## 前提条件

### 必須ツール

- **Terraform**: バージョン1.6.0以上
- **Google Cloud SDK (gcloud CLI)**: 最新版
- **Docker**: 最新版

```bash
# バージョン確認
terraform version
gcloud version
docker --version
```

### 必要な権限

- GCPプロジェクトの作成権限（組織管理者から付与）
- または、既存の本番用プロジェクトへの編集者権限
- 請求先アカウントへのアクセス権限

## 本番用GCPプロジェクトの作成

### 1. プロジェクトIDを確認

デプロイ先のGCPプロジェクトIDを確認します。

```bash
# プロジェクトIDを環境変数に設定
export PROD_PROJECT_ID="natural-ether-481906-c4"
export PROJECT_ID="${PROD_PROJECT_ID}"
```

### 2. デフォルトプロジェクトの設定

```bash
gcloud config set project $PROD_PROJECT_ID
```

## 必要なAPIの有効化

本番環境では、以下のAPIを有効化します。

```bash
# 基本API
gcloud services enable compute.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudtasks.googleapis.com

# IAM関連
gcloud services enable iam.googleapis.com
gcloud services enable iamcredentials.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com

# AI関連
gcloud services enable aiplatform.googleapis.com
```

## Terraformステートバケットの作成

Terraformのステートファイルを保存するためのバケットを作成します。

```bash
# ステート管理用バケットを作成
gsutil mb -p $PROD_PROJECT_ID -l asia-northeast1 gs://${PROD_PROJECT_ID}-terraform-state

# バージョニングを有効化
gsutil versioning set on gs://${PROD_PROJECT_ID}-terraform-state

# バケットのライフサイクル設定（古いバージョンを90日後に削除）
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 10,
          "isLive": false
        }
      }
    ]
  }
}
EOF
gsutil lifecycle set lifecycle.json gs://${PROD_PROJECT_ID}-terraform-state
rm lifecycle.json
```

## Terraform初期化

### 1. Terraformディレクトリに移動

```bash
cd infrastructure/terraform
```

### 2. backend.tfの作成

`backend.tf.example`をコピーして`backend.tf`を作成し、ステートバケット名を設定します。

```bash
# backend.tfを作成
cp backend.tf.example backend.tf

# backend.tfを編集（エディタで開く）
# bucket = "YOUR-PROJECT-ID-terraform-state" を実際のプロジェクトIDに変更
```

編集後の内容例：

```hcl
terraform {
  backend "gcs" {
    bucket = "your-project-id-terraform-state"
    prefix = "terraform/state"
  }
}
```

### 3. Terraformの初期化

```bash
terraform init
```

## 本番環境ワークスペースの作成

```bash
# productionワークスペースを作成
terraform workspace new production

# ワークスペースの確認
terraform workspace list
```

## 本番用変数ファイルの作成

`environments/production.tfvars.example`をコピーして`production.tfvars`を作成し、本番環境の設定を行います。

```bash
# テンプレートからコピー
cp environments/production.tfvars.example environments/production.tfvars
```

以下の値を設定します：

```hcl
# 本番環境のGCPプロジェクトID
prod_project_id = "your-project-id"

# 開発環境の設定（本番環境では不要だが、変数定義のため空文字を設定）
dev_project_id = ""
developer_id   = ""

# リージョンとゾーン（デフォルト: asia-northeast1）
region = "asia-northeast1"
zone   = "asia-northeast1-a"

# 本番ドメイン（未指定時はCORSを全許可）
production_domain = ""

# コストセンター
cost_center = "historical-travel-agent"

# 画像生成実行モード（本番は cloud_tasks 推奨）
image_execution_mode = "cloud_tasks"

# Cloud Tasks設定
cloud_tasks_location = "asia-northeast1"
cloud_tasks_queue_name = "spot-image-generation"
cloud_tasks_max_dispatches_per_second = 5
cloud_tasks_max_concurrent_dispatches = 10
cloud_tasks_max_attempts = 10
cloud_tasks_min_backoff_seconds = 5
cloud_tasks_max_backoff_seconds = 300

# 任意: 固定URLを使う場合のみ指定（通常は空文字で自動解決）
cloud_tasks_target_url = ""
```

## バックエンドDockerイメージのビルド＆プッシュ

本番環境のデプロイ前に、バックエンドアプリケーションのDockerイメージをビルドしてArtifact Registryにプッシュします。

**重要**: Artifact Registryは、Terraformで最初にデプロイする必要があります。以下の手順を実行する前に、一度Terraformでインフラストラクチャの基盤部分をデプロイしてください。

### 事前準備: Artifact Registryの作成

```bash
# Terraformでインフラストラクチャの基盤をデプロイ（初回のみ）
terraform apply -var-file=environments/production.tfvars -target=module.artifact_registry

# 確認してyesを入力
```

### 1. Artifact Registryに認証

```bash
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
```

### 2. バックエンドディレクトリに移動

```bash
cd ../../backend
```

### 3. Dockerイメージをビルド

```bash
# Cloud Run用にlinux/amd64プラットフォームでビルド
docker build --platform linux/amd64 -t asia-northeast1-docker.pkg.dev/${PROJECT_ID}/travel-agent/backend:latest .
```

### 4. Artifact Registryにプッシュ

```bash
docker push asia-northeast1-docker.pkg.dev/${PROJECT_ID}/travel-agent/backend:latest
```

### 5. イメージが正しくプッシュされたか確認

```bash
gcloud artifacts docker images list asia-northeast1-docker.pkg.dev/${PROJECT_ID}/travel-agent
```

以下のような出力が表示されれば成功です：

```
IMAGE                                                                    DIGEST        CREATE_TIME          UPDATE_TIME
asia-northeast1-docker.pkg.dev/your-project-id/travel-agent/backend  sha256:xxxxx  2024-01-27 12:00:00  2024-01-27 12:00:00
```

### 6. Terraformディレクトリに戻る

```bash
cd ../infrastructure/terraform
```

## フロントエンドDockerイメージのビルド＆プッシュ

バックエンドと同様に、フロントエンドアプリケーションのDockerイメージをビルドしてArtifact Registryにプッシュします。

```bash
# バックエンドのみデプロイ（初回のみ）
terraform apply -var-file=environments/production.tfvars -target=module.cloud_run
```

### 1. 環境変数ファイルの作成

```bash
# バックエンドURLを取得
export BACKEND_URL=$(terraform output -raw backend_url)
cd ../../frontend

# .env.productionファイルを作成
cat > .env.production <<EOF
NEXT_PUBLIC_API_URL=/
BACKEND_SERVICE_URL=${BACKEND_URL}
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
EOF
```

### 2. Dockerイメージをビルド

```bash
# Cloud Run用にlinux/amd64プラットフォームでビルド
docker build --platform linux/amd64 -t asia-northeast1-docker.pkg.dev/${PROJECT_ID}/travel-agent/frontend:latest .
```

### 3. Artifact Registryにプッシュ

```bash
docker push asia-northeast1-docker.pkg.dev/${PROJECT_ID}/travel-agent/frontend:latest
```

### 4. イメージが正しくプッシュされたか確認

```bash
gcloud artifacts docker images list asia-northeast1-docker.pkg.dev/${PROJECT_ID}/travel-agent
```

以下のような出力が表示されれば成功です：

```
IMAGE                                                                     DIGEST        CREATE_TIME          UPDATE_TIME
asia-northeast1-docker.pkg.dev/your-project-id/travel-agent/backend   sha256:xxxxx  2024-01-27 12:00:00  2024-01-27 12:00:00
asia-northeast1-docker.pkg.dev/your-project-id/travel-agent/frontend  sha256:xxxxx  2024-01-27 12:00:00  2024-01-27 12:00:00
```

### 5. Terraformディレクトリに戻る

```bash
cd ../infrastructure/terraform
```

## インフラストラクチャのデプロイ

バックエンドとフロントエンドのDockerイメージのプッシュが完了したら、インフラストラクチャ全体をデプロイします。

### 1. プランの確認

```bash
terraform plan -var-file=environments/production.tfvars
```

以下のようなリソースが作成される予定であることを確認します：

- Cloud Storage（アップロード用バケット）
- Artifact Registry（Dockerイメージ用リポジトリ）
- Secret Manager（データベースパスワード）
- Cloud SQL（PostgreSQL 16、db-f1-micro）
- IAM（サービスアカウント、権限）
- Cloud Run（バックエンドサービス）
- Cloud Run（フロントエンドサービス）
- Cloud Tasks（スポット画像生成キュー）

### 2. デプロイの実行

```bash
terraform apply -var-file=environments/production.tfvars
```

`yes`と入力して実行します。

## データベースマイグレーションの実行

Cloud Run Serviceは起動時に自動でマイグレーションを実行しません。  
本番デプロイ後、ローカル端末から本番DBへ直接Alembicマイグレーションを実行します。

```bash
# backendディレクトリで実行
cd ../../backend
uv sync

PROJECT_ID="natural-ether-481906-c4"
DATABASE_HOST="34.180.69.3"
DATABASE_NAME="travel_agent"
DATABASE_USER="backend_user"

DATABASE_URL="" \
DATABASE_HOST="${DATABASE_HOST}" \
DATABASE_NAME="${DATABASE_NAME}" \
DATABASE_USER="${DATABASE_USER}" \
DATABASE_PASSWORD="$(gcloud secrets versions access latest --secret=db-password-production --project=${PROJECT_ID})" \
uv run alembic upgrade head

# 適用リビジョン確認
DATABASE_URL="" \
DATABASE_HOST="${DATABASE_HOST}" \
DATABASE_NAME="${DATABASE_NAME}" \
DATABASE_USER="${DATABASE_USER}" \
DATABASE_PASSWORD="$(gcloud secrets versions access latest --secret=db-password-production --project=${PROJECT_ID})" \
uv run alembic current
```

`DATABASE_PASSWORD` は Secret Manager の `db-password-production` から取得します。  
実行には `roles/secretmanager.secretAccessor` 権限が必要です。
`.env` の `DATABASE_URL` が設定されている場合はそちらが優先されるため、`DATABASE_URL=""` を指定して無効化してください。

## 動作確認

### 1. バックエンドのヘルスチェック

```bash
# バックエンドURLを取得
export BACKEND_URL=$(terraform output -raw backend_url)

# ヘルスチェックエンドポイントにアクセス
curl ${BACKEND_URL}/health
```

成功すると、以下のようなレスポンスが返ります：

```json
{"status":"ok"}
```

### 2. フロントエンドの動作確認

```bash
# フロントエンドURLを取得
export FRONTEND_URL=$(terraform output -raw frontend_url)

# ブラウザで開く
open ${FRONTEND_URL}
```

**確認項目**:
- フロントエンドが正常に表示される
- バックエンドAPIとの通信が正常に動作する
- アプリケーションの機能が正常に動作する

### 3. Cloud Tasksキューの確認

```bash
gcloud tasks queues describe spot-image-generation \
  --location=asia-northeast1 \
  --project=${PROJECT_ID}
```

`state: RUNNING` が表示されることを確認します。

## トラブルシューティング

### Cloud Storage署名URL生成で `iam.serviceAccounts.signBlob` が 403 になる場合

画像生成タスク実行時に以下のエラーが出る場合があります。

- `Permission 'iam.serviceAccounts.signBlob' denied on resource`
- `Error calling the IAM signBytes API`

この場合、Cloud Run実行サービスアカウントに `roles/iam.serviceAccountTokenCreator` が不足しています。

#### 1. 現在の権限を確認

```bash
gcloud iam service-accounts get-iam-policy \
  backend-service-production@natural-ether-481906-c4.iam.gserviceaccount.com \
  --project natural-ether-481906-c4
```

`roles/iam.serviceAccountTokenCreator` に以下メンバーが含まれていることを確認します。

- `serviceAccount:backend-service-production@natural-ether-481906-c4.iam.gserviceaccount.com`

#### 2. 緊急回避として権限を付与

```bash
gcloud iam service-accounts add-iam-policy-binding \
  backend-service-production@natural-ether-481906-c4.iam.gserviceaccount.com \
  --member="serviceAccount:backend-service-production@natural-ether-481906-c4.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --project natural-ether-481906-c4
```

#### 3. 反映確認

```bash
gcloud iam service-accounts get-iam-policy \
  backend-service-production@natural-ether-481906-c4.iam.gserviceaccount.com \
  --project natural-ether-481906-c4
```

#### 4. 恒久対応

手動付与のみだと再作成時に失われる可能性があるため、Terraformで以下を管理します。

- `infrastructure/terraform/modules/iam/main.tf`
- `google_service_account_iam_member.backend_token_creator_self`

必要に応じて以下を実行して本番へ反映してください。

```bash
cd infrastructure/terraform
terraform plan -var-file=environments/production.tfvars
terraform apply -var-file=environments/production.tfvars
```
