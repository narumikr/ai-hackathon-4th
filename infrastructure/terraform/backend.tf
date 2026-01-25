# Terraform State Management
# 
# このファイルは、Terraformのステートファイルを保存するバックエンドを設定します。
# 
# 重要: ステート管理用のCloud Storageバケットは、Terraform実行前に手動で作成する必要があります。
# 
# セットアップ手順:
# 1. GCPプロジェクトを作成
# 2. 以下のコマンドでバケットを作成:
#    gsutil mb -p YOUR-PROD-PROJECT-ID -l asia-northeast1 gs://YOUR-PROD-PROJECT-ID-terraform-state
# 3. バージョニングを有効化:
#    gsutil versioning set on gs://YOUR-PROD-PROJECT-ID-terraform-state
# 4. 下記のbucket値を実際のバケット名に置き換える

terraform {
  backend "gcs" {
    bucket = "YOUR-PROD-PROJECT-ID-terraform-state"
    prefix = "terraform/state"
  }
}
