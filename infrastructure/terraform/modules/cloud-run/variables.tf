# Cloud Runモジュールの変数定義

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
  description = "コンテナイメージのURL"
  type        = string
}

variable "storage_bucket_name" {
  description = "Cloud Storageバケット名"
  type        = string
}

variable "database_host" {
  description = "データベースホスト（Cloud SQLのパブリックIP）"
  type        = string
}

variable "database_name" {
  description = "データベース名"
  type        = string
}

variable "database_user" {
  description = "データベースユーザー名"
  type        = string
}

variable "db_password_secret_id" {
  description = "データベースパスワードのシークレットID"
  type        = string
}

variable "service_account_email" {
  description = "サービスアカウントのメールアドレス"
  type        = string
}

variable "frontend_service_account_email" {
  description = "フロントエンド用サービスアカウントのメールアドレス"
  type        = string
}

variable "labels" {
  description = "リソースに付与するラベル"
  type        = map(string)
  default     = {}
}

variable "image_execution_mode" {
  description = "画像生成実行モード（local_worker または cloud_tasks）"
  type        = string
  default     = "local_worker"
}

variable "cloud_tasks_location" {
  description = "Cloud Tasksのロケーション"
  type        = string
  default     = ""
}

variable "cloud_tasks_queue_name" {
  description = "Cloud Tasksキュー名"
  type        = string
  default     = ""
}

variable "cloud_tasks_target_url" {
  description = "Cloud TasksのHTTPターゲットURL"
  type        = string
  default     = ""
}

variable "cloud_tasks_service_account_email" {
  description = "Cloud Tasks OIDCトークン発行に使用するサービスアカウント"
  type        = string
  default     = ""
}

variable "cloud_tasks_dispatch_deadline_seconds" {
  description = "Cloud Tasksのdispatch deadline秒数"
  type        = number
  default     = 1800
}
