# Artifact Registryモジュール
# Dockerイメージを保存するためのリポジトリを管理

# Dockerイメージ用リポジトリ
resource "google_artifact_registry_repository" "docker" {
  count         = var.environment == "production" ? 1 : 0
  location      = var.region
  repository_id = "travel-agent"
  description   = "Docker images for Historical Travel Agent"
  format        = "DOCKER"

  # 脆弱性スキャン設定
  docker_config {
    immutable_tags = false
  }

  # ラベル
  labels = var.labels
}

# 脆弱性スキャン用のIAM権限
# Artifact Registryサービスアカウントにreader権限を付与
resource "google_artifact_registry_repository_iam_member" "vulnerability_scanner" {
  count      = var.environment == "production" ? 1 : 0
  location   = google_artifact_registry_repository.docker[0].location
  repository = google_artifact_registry_repository.docker[0].name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:service-${var.project_number}@gcp-sa-artifactregistry.iam.gserviceaccount.com"
}
