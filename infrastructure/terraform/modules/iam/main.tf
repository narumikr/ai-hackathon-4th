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

# Cloud Tasks enqueue権限
resource "google_project_iam_member" "backend_cloud_tasks_enqueuer" {
  count   = var.environment == "production" ? 1 : 0
  project = var.project_id
  role    = "roles/cloudtasks.enqueuer"
  member  = "serviceAccount:${google_service_account.backend[0].email}"
}

# Cloud TasksサービスエージェントがOIDCトークンを発行するための権限
resource "google_service_account_iam_member" "cloud_tasks_token_creator" {
  count              = var.environment == "production" ? 1 : 0
  service_account_id = google_service_account.backend[0].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${var.project_number}@gcp-sa-cloudtasks.iam.gserviceaccount.com"
}

# Cloud Runバックエンド自身が署名URL生成でIAM Credentialsを利用できるようにする権限
resource "google_service_account_iam_member" "backend_token_creator_self" {
  count              = var.environment == "production" ? 1 : 0
  service_account_id = google_service_account.backend[0].name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.backend[0].email}"
}

# Cloud RunバックエンドがCloud Tasksを作成する際、OIDCトークン発行用SAをactAsできるようにする権限
resource "google_service_account_iam_member" "backend_service_account_user" {
  count              = var.environment == "production" ? 1 : 0
  service_account_id = google_service_account.backend[0].name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.backend[0].email}"
}

# Firebase Auth権限（IDトークン検証）
resource "google_project_iam_member" "backend_firebase_auth" {
  count   = var.environment == "production" ? 1 : 0
  project = var.project_id
  role    = "roles/firebaseauth.viewer"
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
