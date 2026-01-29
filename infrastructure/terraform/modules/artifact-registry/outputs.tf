# Artifact Registryモジュールの出力値

output "repository_id" {
  description = "Artifact RegistryリポジトリのID"
  value       = var.environment == "production" ? google_artifact_registry_repository.docker[0].repository_id : null
}

output "repository_url" {
  description = "Artifact RegistryリポジトリのURL"
  value       = var.environment == "production" ? "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker[0].repository_id}" : null
}

output "repository_name" {
  description = "Artifact Registryリポジトリの完全名"
  value       = var.environment == "production" ? google_artifact_registry_repository.docker[0].name : null
}
