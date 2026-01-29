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

variable "labels" {
  description = "リソースに付与するラベル"
  type        = map(string)
  default     = {}
}
