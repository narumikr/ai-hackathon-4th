variable "environment" {
  description = "環境名（development または production）"
  type        = string
}

variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "location" {
  description = "Cloud Tasksのロケーション"
  type        = string
}

variable "queue_name" {
  description = "Cloud Tasksキュー名"
  type        = string
}

variable "max_dispatches_per_second" {
  description = "1秒あたり最大dispatch数"
  type        = number
  default     = 5
}

variable "max_concurrent_dispatches" {
  description = "同時dispatch上限"
  type        = number
  default     = 10
}

variable "max_attempts" {
  description = "最大リトライ回数"
  type        = number
  default     = 10
}

variable "min_backoff_seconds" {
  description = "最小バックオフ秒数"
  type        = number
  default     = 5
}

variable "max_backoff_seconds" {
  description = "最大バックオフ秒数"
  type        = number
  default     = 300
}
