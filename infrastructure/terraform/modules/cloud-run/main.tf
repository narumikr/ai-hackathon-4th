# Cloud Runモジュール
# FastAPIバックエンドアプリケーションをホスティング

# Cloud Runサービス
resource "google_cloud_run_service" "backend" {
  count    = var.environment == "production" ? 1 : 0
  name     = "historical-travel-agent-backend-${var.environment}"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        # Artifact Registryからイメージを取得
        image = var.container_image

        # 環境変数
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }

        env {
          name  = "GOOGLE_CLOUD_LOCATION"
          value = var.region
        }

        env {
          name  = "STORAGE_TYPE"
          value = "gcs"
        }

        env {
          name  = "GCS_BUCKET_NAME"
          value = var.storage_bucket_name
        }

        # データベース接続設定（個別の環境変数）
        env {
          name  = "DATABASE_HOST"
          value = var.database_host
        }

        env {
          name  = "DATABASE_NAME"
          value = var.database_name
        }

        env {
          name  = "DATABASE_USER"
          value = var.database_user
        }

        # データベースパスワードをSecret Managerから取得
        # Cloud RunのSecret Manager統合機能を使用
        env {
          name = "DATABASE_PASSWORD"
          value_from {
            secret_key_ref {
              name = var.db_password_secret_id
              key  = "latest"
            }
          }
        }

        # リソース制限
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        # ヘルスチェック
        liveness_probe {
          http_get {
            path = "/health"
          }
          initial_delay_seconds = 10
          period_seconds        = 10
          timeout_seconds       = 5
          failure_threshold     = 3
        }

        # 起動プローブ
        startup_probe {
          http_get {
            path = "/health"
          }
          initial_delay_seconds = 0
          period_seconds        = 10
          timeout_seconds       = 5
          failure_threshold     = 3
        }
      }

      # サービスアカウント
      service_account_name = var.service_account_email

      # スケーリング設定
      container_concurrency = 80
    }

    metadata {
      annotations = {
        # 自動スケーリング設定
        "autoscaling.knative.dev/minScale" = "0"
        "autoscaling.knative.dev/maxScale" = "100"
        # CPU割り当て（リクエスト処理中のみCPUを使用）
        "run.googleapis.com/cpu-throttling" = "true"
      }
      labels = var.labels
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  # 自動的にHTTPSを有効化
  autogenerate_revision_name = true
}

# パブリックアクセス許可（一般公開）
resource "google_cloud_run_service_iam_member" "backend_public" {
  count    = var.environment == "production" ? 1 : 0
  service  = google_cloud_run_service.backend[0].name
  location = google_cloud_run_service.backend[0].location
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}
