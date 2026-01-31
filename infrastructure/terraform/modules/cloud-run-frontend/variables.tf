# Cloud Run Frontendモジュールの変数定義

variable "environment" {
  description = "環境名（development または production）"
  type        = string
}

variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "region" {
  description = "GCPリージョン"
  type        = string
}

variable "container_image" {
  description = "コンテナイメージのURL（例: asia-northeast1-docker.pkg.dev/project-id/repository/frontend:latest）"
  type        = string
}

variable "backend_service_url" {
  description = "バックエンドAPIのURL（NEXT_PUBLIC_API_URL環境変数に設定される）"
  type        = string
}

variable "service_account_email" {
  description = "フロントエンドサービスが使用するサービスアカウントのメールアドレス"
  type        = string
}

variable "labels" {
  description = "リソースに付与するラベル（environment, managed_by, project等）"
  type        = map(string)
  default     = {}
}
