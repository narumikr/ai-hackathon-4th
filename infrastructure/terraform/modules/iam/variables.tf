# IAMモジュールの変数定義

variable "environment" {
  description = "環境名（development または production）"
  type        = string
}

variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "project_number" {
  description = "GCPプロジェクト番号"
  type        = string
}

variable "region" {
  description = "GCPリージョン"
  type        = string
}

variable "storage_bucket_name" {
  description = "Cloud Storageバケット名（バックエンド用）"
  type        = string
  default     = ""
}

variable "db_password_secret_id" {
  description = "データベースパスワードのシークレットID"
  type        = string
  default     = ""
}

variable "artifact_registry_repository_id" {
  description = "Artifact RegistryリポジトリID"
  type        = string
  default     = ""
}
