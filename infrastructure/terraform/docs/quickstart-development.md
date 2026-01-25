# 開発環境クイックスタートガイド

このガイドは、最小限の手順で個人用Cloud Storageバケットを作成する方法を説明します。

## 前提条件

- Terraform 1.6.0以上がインストールされていること
- gcloud CLIがインストールされていること
- Google Cloudアカウントを持っていること

## セットアップ手順

### 1. GCPプロジェクトを作成

[GCP Console](https://console.cloud.google.com/) でプロジェクトを作成し、プロジェクトIDをメモしてください。

### 2. 環境変数を設定

以下のコマンドを実行する前に、環境変数を設定します：

```bash
# あなたのGCPプロジェクトIDに置き換えてください
export DEV_PROJECT_ID="your-dev-project-id"

# あなたの名前に置き換えてください（英数字とハイフンのみ、小文字推奨）
export DEVELOPER_ID="your-name"
```

### 3. コマンドを実行

以下のコマンドをコピー&ペーストして実行してください：

```bash
# 1. gcloud認証とプロジェクト設定
gcloud auth login
gcloud config set project ${DEV_PROJECT_ID}

# 2. APIを有効化
gcloud services enable storage.googleapis.com

# 3. ステートバケットを作成
gsutil mb -p ${DEV_PROJECT_ID} -l asia-northeast1 gs://${DEV_PROJECT_ID}-terraform-state
gsutil versioning set on gs://${DEV_PROJECT_ID}-terraform-state

# 4. backend.tfを作成（開発環境用テンプレートをコピー）
cd infrastructure/terraform
cp backend-template.tfbackend backend-${DEVELOPER_ID}.tfbackend

# 5. backend.tfを編集（バケット名を置き換え）
sed -i.bak "s/YOUR-DEV-PROJECT-ID/${DEV_PROJECT_ID}/g" backend-${DEVELOPER_ID}.tfbackend

# 6. Terraformを初期化
terraform init -backend-config=backend-${DEVELOPER_ID}.tfbackend

# 7. 開発用ワークスペースを作成
terraform workspace new development

# 8. 変数ファイルを作成
cp environments/dev-template.tfvars environments/dev-${DEVELOPER_ID}.tfvars

# 8. 変数ファイルを編集（プロジェクトIDと開発者IDを置き換え）
cat > environments/dev-${DEVELOPER_ID}.tfvars <<EOF
# 開発環境のGCPプロジェクトID
dev_project_id = "${DEV_PROJECT_ID}"

# 開発者の識別子
developer_id = "${DEVELOPER_ID}"

# 以下の変数は開発環境では使用されません
prod_project_id               = ""
production_domain             = ""
github_repository             = ""
github_workload_identity_pool = ""
EOF

# 9. プランを確認
terraform plan -var-file=environments/dev-${DEVELOPER_ID}.tfvars

# 10. デプロイを実行
terraform apply -var-file=environments/dev-${DEVELOPER_ID}.tfvars
```

### 4. 確認

デプロイが成功したら、以下のコマンドでバケットを確認できます：

```bash
# バケット一覧を表示
gsutil ls
```
