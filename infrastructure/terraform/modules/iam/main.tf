# IAMモジュール
# サービスアカウントと権限管理

# ============================================================================
# バックエンド用サービスアカウント
# ============================================================================

# バックエンド用サービスアカウント
resource "google_service_account" "backend" {
  count        = var.environment == "production" ? 1 : 0
  account_id   = "backend-service-${var.environment}"
  display_name = "Backend Service Account"
  project      = var.project_id
  description  = "Cloud Runバックエンドサービス用のサービスアカウント"
}

# Cloud SQL Client権限
resource "google_project_iam_member" "backend_sql_client" {
  count   = var.environment == "production" ? 1 : 0
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend[0].email}"
}

# Cloud Storage権限（アップロードバケット用）
resource "google_storage_bucket_iam_member" "backend_storage" {
  count  = var.environment == "production" ? 1 : 0
  bucket = var.storage_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.backend[0].email}"
}

# Secret Manager権限（データベースパスワードのみ）
resource "google_secret_manager_secret_iam_member" "backend_secret_accessor" {
  count     = var.environment == "production" ? 1 : 0
  project   = var.project_id
  secret_id = var.db_password_secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.backend[0].email}"
}

# Vertex AI User権限（Gemini API使用）
resource "google_project_iam_member" "backend_vertex_ai" {
  count   = var.environment == "production" ? 1 : 0
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.backend[0].email}"
}

# ============================================================================
# フロントエンド用サービスアカウント
# ============================================================================

# フロントエンド用サービスアカウント
resource "google_service_account" "frontend" {
  count        = var.environment == "production" ? 1 : 0
  account_id   = "frontend-service-account"
  display_name = "Frontend Service Account"
  project      = var.project_id
  description  = "Service account for Cloud Run frontend service"
}


