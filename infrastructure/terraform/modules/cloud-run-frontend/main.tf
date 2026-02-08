# Cloud Run Frontendモジュール
# Next.jsフロントエンドアプリケーションをホスティング

# Cloud Runサービス
resource "google_cloud_run_service" "frontend" {
  count    = var.environment == "production" ? 1 : 0
  name     = "historical-travel-agent-frontend-production"
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        # Artifact Registryからイメージを取得
        image = var.container_image

        # 環境変数
        env {
          name  = "NEXT_PUBLIC_API_URL"
          value = "/"
        }

        env {
          name  = "BACKEND_SERVICE_URL"
          value = var.backend_service_url
        }

        env {
          name  = "NODE_ENV"
          value = "production"
        }

        env {
          name  = "NEXT_TELEMETRY_DISABLED"
          value = "1"
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
            path = "/"
          }
          initial_delay_seconds = 10
          period_seconds        = 10
          timeout_seconds       = 5
          failure_threshold     = 3
        }

        # 起動プローブ
        startup_probe {
          http_get {
            path = "/"
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
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  # ラベル設定
  metadata {
    labels = var.labels
  }

  # 自動的にHTTPSを有効化
  autogenerate_revision_name = true
}

# パブリックアクセス許可（一般公開）
resource "google_cloud_run_service_iam_member" "frontend_public" {
  count    = var.environment == "production" ? 1 : 0
  service  = google_cloud_run_service.frontend[0].name
  location = google_cloud_run_service.frontend[0].location
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "allUsers"
}
