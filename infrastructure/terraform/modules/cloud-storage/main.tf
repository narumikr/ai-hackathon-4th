# Cloud Storage Module
# 
# このモジュールは、環境に応じてCloud Storageバケットを作成します。
# - development: 開発者個人用バケット（30日で自動削除）
# - production: アップロードファイル用バケット（365日で自動削除）

# 開発環境用バケット
resource "google_storage_bucket" "dev_personal" {
  count    = var.environment == "development" ? 1 : 0
  name     = "${var.developer_id}-travel-agent-dev"
  location = var.region
  project  = var.project_id

  # 均一なバケットレベルのアクセス
  uniform_bucket_level_access = true

  # バージョニング有効化
  versioning {
    enabled = true
  }

  # ライフサイクルルール（30日で自動削除）
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  # CORS設定（ローカル開発環境からのアクセス許可）
  cors {
    origin          = ["http://localhost:3000"]
    method          = ["GET", "POST", "PUT", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  # ラベル
  labels = var.labels

  # 強制削除を許可（開発環境のため）
  force_destroy = true
}

# 本番環境用バケット
resource "google_storage_bucket" "production" {
  count    = var.environment == "production" ? 1 : 0
  name     = "${var.project_id}-travel-uploads"
  location = var.region
  project  = var.project_id

  # 均一なバケットレベルのアクセス
  uniform_bucket_level_access = true

  # ライフサイクルルール（365日で自動削除）
  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  # CORS設定（本番ドメインからのアクセス許可）
  cors {
    origin          = ["https://${var.domain}"]
    method          = ["GET", "POST", "PUT", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  # ラベル
  labels = var.labels

  # 本番環境では誤削除防止のため force_destroy は false（デフォルト）
}
