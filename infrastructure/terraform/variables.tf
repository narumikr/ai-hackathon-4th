# Variables for GCP Terraform Infrastructure

# プロジェクトID
variable "dev_project_id" {
  description = "開発環境のGCPプロジェクトID"
  type        = string
  default     = ""
}

variable "prod_project_id" {
  description = "本番環境のGCPプロジェクトID"
  type        = string
  default     = ""
}

# リージョンとゾーン
variable "region" {
  description = "GCPリージョン"
  type        = string
  default     = "asia-northeast1"
}

variable "zone" {
  description = "GCPゾーン"
  type        = string
  default     = "asia-northeast1-a"
}

# 開発者ID（開発環境用）
variable "developer_id" {
  description = "開発者の識別子（バケット名に使用）。英数字とハイフンのみ、小文字推奨"
  type        = string
  default     = ""
}

# 本番ドメイン
variable "production_domain" {
  description = "本番環境のドメイン名"
  type        = string
  default     = ""
}

# コストセンター
variable "cost_center" {
  description = "コストセンターのラベル値"
  type        = string
  default     = "historical-travel-agent"
}

variable "image_execution_mode" {
  description = "画像生成実行モード（local_worker または cloud_tasks）"
  type        = string
  default     = "local_worker"
}

variable "cloud_tasks_location" {
  description = "Cloud Tasksロケーション"
  type        = string
  default     = "asia-northeast1"
}

variable "cloud_tasks_queue_name" {
  description = "Cloud Tasksキュー名"
  type        = string
  default     = "spot-image-generation"
}

variable "cloud_tasks_target_url" {
  description = "Cloud TasksのHTTPターゲットURL"
  type        = string
  default     = ""
}

variable "cloud_tasks_max_dispatches_per_second" {
  description = "Cloud Tasksの1秒あたり最大dispatch数"
  type        = number
  default     = 5
}

variable "cloud_tasks_max_concurrent_dispatches" {
  description = "Cloud Tasksの同時dispatch上限"
  type        = number
  default     = 10
}

variable "cloud_tasks_max_attempts" {
  description = "Cloud Tasksの最大リトライ回数"
  type        = number
  default     = 10
}

variable "cloud_tasks_min_backoff_seconds" {
  description = "Cloud Tasksの最小バックオフ秒数"
  type        = number
  default     = 5
}

variable "cloud_tasks_max_backoff_seconds" {
  description = "Cloud Tasksの最大バックオフ秒数"
  type        = number
  default     = 300
}
