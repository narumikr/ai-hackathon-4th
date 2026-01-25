# 開発環境セットアップ手順書

このドキュメントは、開発者が個人用のCloud Storageバケットを作成するための手順を説明します。

## 目次

1. [前提条件](#前提条件)
2. [GCPプロジェクトの作成](#gcpプロジェクトの作成)
3. [APIの有効化](#apiの有効化)
4. [ステートバケットの作成](#ステートバケットの作成)
5. [Terraformの初期化](#terraformの初期化)
6. [ワークスペースの作成](#ワークスペースの作成)
7. [変数ファイルの作成](#変数ファイルの作成)
8. [開発環境のデプロイ](#開発環境のデプロイ)
9. [動作確認](#動作確認)
10. [クリーンアップ](#クリーンアップ)

## 前提条件

以下のツールがインストールされていることを確認してください。

### 必須ツール

- **Terraform**: バージョン 1.6.0 以上
  ```bash
  terraform version
  ```
  
  インストール方法: https://developer.hashicorp.com/terraform/downloads

- **Google Cloud SDK (gcloud CLI)**: 最新版
  ```bash
  gcloud version
  ```
  
  インストール方法: https://cloud.google.com/sdk/docs/install

### GCPアカウント

- Google Cloudアカウントを持っていること
- プロジェクトを作成する権限があること

## GCPプロジェクトの作成

開発用のGCPプロジェクトを作成します。

### 1. GCPコンソールでプロジェクトを作成

1. [GCP Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトセレクターをクリック
3. 「新しいプロジェクト」をクリック
4. プロジェクト名を入力（例: `my-travel-agent-dev`）
5. 「作成」をクリック

### 2. プロジェクトIDを確認

プロジェクトIDをメモしてください。後の手順で使用します。

```bash
# プロジェクトIDの例
# my-travel-agent-dev-123456
```

### 3. gcloud CLIでプロジェクトを設定

```bash
# 認証（初回のみ）
gcloud auth login

# プロジェクトを設定
gcloud config set project YOUR-DEV-PROJECT-ID
```

## APIの有効化

開発環境では、Cloud Storage APIのみ有効化します。

```bash
# Cloud Storage APIを有効化
gcloud services enable storage.googleapis.com
```

## ステートバケットの作成

Terraformのステートファイルを保存するバケットを作成します。

**重要**: このバケットは、Terraformで管理せず、手動で作成します。

```bash
# ステート管理用バケットを作成
gsutil mb -p YOUR-DEV-PROJECT-ID -l asia-northeast1 gs://YOUR-DEV-PROJECT-ID-terraform-state

# バージョニングを有効化
gsutil versioning set on gs://YOUR-DEV-PROJECT-ID-terraform-state
```

## Terraformの初期化

### 1. backend.tfを編集

`infrastructure/terraform/backend.tf` を開き、バケット名を実際のプロジェクトIDに置き換えます。

```hcl
terraform {
  backend "gcs" {
    bucket = "YOUR-DEV-PROJECT-ID-terraform-state"  # ← ここを変更
    prefix = "terraform/state"
  }
}
```

### 2. Terraformを初期化

```bash
cd infrastructure/terraform
terraform init
```

成功すると、以下のようなメッセージが表示されます：

```
Terraform has been successfully initialized!
```

## ワークスペースの作成

開発環境用のワークスペースを作成します。

```bash
# developmentワークスペースを作成
terraform workspace new development

# ワークスペース一覧を確認
terraform workspace list
```

現在のワークスペースが `development` になっていることを確認してください。

```bash
# 現在のワークスペースを確認
terraform workspace show
# 出力: development
```

## 変数ファイルの作成

個人用の変数ファイルを作成します。

### 1. テンプレートをコピー

```bash
cd infrastructure/terraform
cp environments/development-template.tfvars environments/development-$(whoami).tfvars
```

### 2. 変数ファイルを編集

`environments/development-YOUR-NAME.tfvars` を開き、以下の値を設定します：

```hcl
# 開発環境のGCPプロジェクトID
dev_project_id = "YOUR-DEV-PROJECT-ID"  # ← 実際のプロジェクトIDに変更

# 開発者の識別子（英数字とハイフンのみ、小文字推奨）
# この値はCloud Storageバケット名に使用されます
developer_id = "your-name"  # ← あなたの名前に変更（例: "alice", "bob"）

# 以下の変数は開発環境では使用されませんが、変数定義のため空文字を設定
prod_project_id               = ""
production_domain             = ""
github_repository             = ""
github_workload_identity_pool = ""
```

**注意**: `developer_id` は、Cloud Storageバケット名に使用されるため、以下のルールに従ってください：
- 英数字とハイフン（`-`）のみ使用可能
- 小文字推奨
- 3〜63文字
- 例: `alice`, `bob`, `dev-team-member-1`

## 開発環境のデプロイ

### 1. プランの確認

まず、Terraformが何を作成するか確認します。

```bash
terraform plan -var-file=environments/development-$(whoami).tfvars
```

以下のリソースが作成される予定であることを確認してください：
- `google_storage_bucket.dev_personal[0]`: 個人用Cloud Storageバケット

### 2. デプロイの実行

問題がなければ、デプロイを実行します。

```bash
terraform apply -var-file=environments/development-$(whoami).tfvars
```

確認メッセージが表示されたら、`yes` と入力してEnterを押します。

```
Do you want to perform these actions in workspace "development"?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

成功すると、以下のような出力が表示されます：

```
Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

development_bucket_name = "your-name-travel-agent-dev"
development_bucket_url = "gs://your-name-travel-agent-dev"
project_id = "YOUR-DEV-PROJECT-ID"
workspace = "development"
```

## 動作確認

### 1. バケットの確認

作成されたバケットを確認します。

```bash
# バケット一覧を表示
gsutil ls

# バケットの詳細を表示
gsutil ls -L gs://YOUR-NAME-travel-agent-dev
```

### 2. ファイルのアップロードテスト

テストファイルをアップロードしてみます。

```bash
# テストファイルを作成
echo "Hello, Cloud Storage!" > test.txt

# バケットにアップロード
gsutil cp test.txt gs://YOUR-NAME-travel-agent-dev/

# アップロードされたファイルを確認
gsutil ls gs://YOUR-NAME-travel-agent-dev/

# ファイルをダウンロード
gsutil cp gs://YOUR-NAME-travel-agent-dev/test.txt downloaded-test.txt

# 内容を確認
cat downloaded-test.txt

# テストファイルを削除
rm test.txt downloaded-test.txt
gsutil rm gs://YOUR-NAME-travel-agent-dev/test.txt
```

### 3. Terraform出力の確認

Terraformの出力値を確認します。

```bash
terraform output
```

## クリーンアップ

開発環境が不要になった場合、リソースを削除できます。

### リソースの削除

```bash
# developmentワークスペースに切り替え（念のため確認）
terraform workspace select development

# リソースを削除
terraform destroy -var-file=environments/development-$(whoami).tfvars
```

確認メッセージが表示されたら、`yes` と入力してEnterを押します。

**注意**: バケット内にファイルがある場合でも、`force_destroy = true` が設定されているため、バケットごと削除されます。

### ステートバケットの削除（オプション）

Terraformを完全に削除する場合は、ステートバケットも削除できます。

```bash
# ステートバケットを削除
gsutil rm -r gs://YOUR-DEV-PROJECT-ID-terraform-state
```

### プロジェクトの削除（オプション）

GCPプロジェクト全体を削除する場合：

```bash
gcloud projects delete YOUR-DEV-PROJECT-ID
```

## トラブルシューティング

### エラー: "Error 403: PROJECT_ID does not exist"

**原因**: プロジェクトIDが間違っているか、プロジェクトが存在しません。

**対処**:
1. プロジェクトIDを確認: `gcloud projects list`
2. `environments/development-YOUR-NAME.tfvars` のプロジェクトIDを修正

### エラー: "Error 403: Cloud Storage API has not been used"

**原因**: Cloud Storage APIが有効化されていません。

**対処**:
```bash
gcloud services enable storage.googleapis.com
```

### エラー: "Error: Invalid bucket name"

**原因**: `developer_id` に使用できない文字が含まれています。

**対処**:
- 英数字とハイフン（`-`）のみ使用
- 小文字に変更
- 3〜63文字の範囲内

### エラー: "Error acquiring the state lock"

**原因**: 別のTerraform実行がステートファイルをロックしています。

**対処**:
1. 他のTerraform実行が完了するまで待つ
2. 強制的にロックを解除（注意が必要）:
   ```bash
   terraform force-unlock LOCK_ID
   ```

## 次のステップ

開発環境のセットアップが完了しました！

- バックエンドアプリケーションから個人用バケットを使用する設定を行ってください
- 本番環境のセットアップについては、`setup-production.md` を参照してください

## 参考リンク

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference)
