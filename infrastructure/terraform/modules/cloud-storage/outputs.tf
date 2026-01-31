# Outputs for Cloud Storage Module

output "bucket_name" {
  description = "バケット名（環境に応じて開発または本番）"
  value       = var.environment == "production" && length(google_storage_bucket.production) > 0 ? google_storage_bucket.production[0].name : (var.environment == "development" && length(google_storage_bucket.dev_personal) > 0 ? google_storage_bucket.dev_personal[0].name : null)
}

output "development_bucket_name" {
  description = "開発環境用バケット名"
  value       = var.environment == "development" && length(google_storage_bucket.dev_personal) > 0 ? google_storage_bucket.dev_personal[0].name : null
}

output "development_bucket_url" {
  description = "開発環境用バケットURL"
  value       = var.environment == "development" && length(google_storage_bucket.dev_personal) > 0 ? google_storage_bucket.dev_personal[0].url : null
}

output "production_bucket_name" {
  description = "本番環境用バケット名"
  value       = var.environment == "production" && length(google_storage_bucket.production) > 0 ? google_storage_bucket.production[0].name : null
}

output "production_bucket_url" {
  description = "本番環境用バケットURL"
  value       = var.environment == "production" && length(google_storage_bucket.production) > 0 ? google_storage_bucket.production[0].url : null
}
