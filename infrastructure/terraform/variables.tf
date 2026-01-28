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

# コストセンター
variable "cost_center" {
  description = "コストセンターのラベル値"
  type        = string
  default     = "historical-travel-agent"
}
