# Cloud SQLモジュール
# PostgreSQLデータベースを管理

# Cloud SQLインスタンス
resource "google_sql_database_instance" "main" {
  count            = var.environment == "production" ? 1 : 0
  name             = "travel-agent-db-${var.environment}"
  database_version = "POSTGRES_16"
  region           = var.region
  project          = var.project_id

  settings {
    tier    = "db-f1-micro" # 最小インスタンス（コスト最適化）
    edition = "ENTERPRISE"  # db-f1-microを使用するため

    # パブリックIP設定（VPCは使用しない）
    ip_configuration {
      ipv4_enabled = true
      ssl_mode     = "ENCRYPTED_ONLY" # SSL/TLS必須

      # 全IPアドレスからのアクセスを許可
      # 注意: 本番運用では特定のIPアドレスのみ許可すべき
      authorized_networks {
        name  = "allow-all"
        value = "0.0.0.0/0"
      }
    }

    # ディスク設定
    disk_type = "PD_SSD"
    disk_size = 10 # 10GB（最小）

    # 自動バックアップ無効（コスト最適化）
    backup_configuration {
      enabled = false
    }

    # メンテナンスウィンドウ
    maintenance_window {
      day          = 7 # 日曜日
      hour         = 3 # 午前3時（JST午後12時）
      update_track = "stable"
    }

    # データベースフラグ
    database_flags {
      name  = "max_connections"
      value = "100"
    }

    # ユーザーラベル
    user_labels = var.labels
  }

  # 誤削除防止
  deletion_protection = false
}

# データベース作成
resource "google_sql_database" "main" {
  count    = var.environment == "production" ? 1 : 0
  name     = "travel_agent"
  instance = google_sql_database_instance.main[0].name
  project  = var.project_id
}

# ユーザー作成
resource "google_sql_user" "backend" {
  count    = var.environment == "production" ? 1 : 0
  name     = "backend_user"
  instance = google_sql_database_instance.main[0].name
  password = var.db_password
  project  = var.project_id
}
