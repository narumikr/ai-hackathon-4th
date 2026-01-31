# Secret Managerモジュールの変数定義

variable "environment" {
  description = "環境名（development または production）"
  type        = string
}

variable "project_id" {
  description = "GCPプロジェクトID"
  type        = string
}

variable "labels" {
  description = "リソースに付与するラベル"
  type        = map(string)
  default     = {}
}
