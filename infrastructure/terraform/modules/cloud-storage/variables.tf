# Variables for Cloud Storage Module

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

variable "developer_id" {
  description = "開発者の識別子（開発環境用バケット名に使用）"
  type        = string
  default     = ""
}

variable "domain" {
  description = "本番環境のドメイン名（CORS設定に使用）"
  type        = string
  default     = ""
}

variable "labels" {
  description = "リソースに付与する共通ラベル"
  type        = map(string)
  default     = {}
}
