# Secret Managerモジュール
# データベースパスワードなどの機密情報を管理

# ランダムパスワード生成
resource "random_password" "db_password" {
  count   = var.environment == "production" ? 1 : 0
  length  = 32
  special = true
  # 特殊文字の種類を制限（PostgreSQLで問題が起きにくい文字のみ）
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

# データベースパスワード用シークレット
resource "google_secret_manager_secret" "db_password" {
  count     = var.environment == "production" ? 1 : 0
  secret_id = "db-password-${var.environment}"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

# シークレットバージョン（パスワードの実際の値を保存）
resource "google_secret_manager_secret_version" "db_password" {
  count       = var.environment == "production" ? 1 : 0
  secret      = google_secret_manager_secret.db_password[0].id
  secret_data = random_password.db_password[0].result
}
