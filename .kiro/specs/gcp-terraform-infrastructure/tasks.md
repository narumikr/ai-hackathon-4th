# タスクリスト: GCP Terraform Infrastructure

## 1. プロジェクト構造とベースファイルの作成

- [x] 1.1 Terraformディレクトリ構造を作成する
  - `infrastructure/terraform/`ディレクトリを作成
  - `infrastructure/terraform/modules/`ディレクトリを作成
  - `infrastructure/terraform/environments/`ディレクトリを作成
  - `infrastructure/terraform/docs/`ディレクトリを作成
  - **Validates: Requirements 1.1, 14.1**

- [x] 1.2 Terraformバージョン管理ファイルを作成する
  - `infrastructure/terraform/versions.tf`を作成
  - Terraform 1.6.0以上を指定
  - Google Provider 5.0以上を指定
  - **Validates: Requirements 14.2**

- [x] 1.3 バックエンド設定ファイルを作成する
  - `infrastructure/terraform/backend.tf`を作成
  - Cloud Storageバックエンドを設定（バケット名はプレースホルダー）
  - **Validates: Requirements 11.1, 11.2, 11.3**

- [x] 1.4 変数定義ファイルを作成する
  - `infrastructure/terraform/variables.tf`を作成
  - dev_project_id、prod_project_id、developer_id、production_domain、github_repository、github_workload_identity_pool変数を定義
  - 各変数に説明とデフォルト値を設定
  - **Validates: Requirements 1.2**

- [x] 1.5 出力値定義ファイルを作成する
  - `infrastructure/terraform/outputs.tf`を作成
  - backend_url、database_connection_name、storage_bucket_name、artifact_registry_url、backend_service_account_email出力を定義
  - **Validates: Requirements 14.4**

- [x] 1.6 変数値のサンプルファイルを作成する
  - `infrastructure/terraform/terraform.tfvars.example`を作成
  - `infrastructure/terraform/environments/development-template.tfvars`を作成
  - `infrastructure/terraform/environments/production.tfvars`を作成（実際の値は含めない）
  - **Validates: Requirements 14.3**

- [x] 1.7 .gitignoreファイルを更新する
  - ルートの`.gitignore`にTerraform関連のパターンを追加
  - *.tfstate、*.tfstate.backup、.terraform/、terraform.tfvars、environments/development-*.tfvarsを追加
  - **Validates: Requirements 11.5**


## 2. メインTerraform設定の実装

- [x] 2.1 main.tfでワークスペース管理を実装する
  - `infrastructure/terraform/main.tf`を作成
  - terraform.workspaceを使用してワークスペース名を取得
  - locals blockで環境ごとの設定（development/production）を定義
  - 現在のワークスペースの設定を取得するlocal変数を定義
  - **Validates: Requirements 1.1, 1.2**

- [x] 2.2 main.tfでリソースタグ/ラベルの共通設定を実装する
  - locals blockで共通ラベルを定義
  - environment（ワークスペース名）ラベルを設定
  - cost_centerラベルを設定
  - **Validates: Requirements 1.4, 12.5**

- [x] 2.3 main.tfでGoogle Providerを設定する
  - provider "google" blockを追加
  - プロジェクトID、リージョン、ゾーンを設定
  - **Validates: Requirements 1.2**


## 3. Cloud Storageモジュールの実装

- [x] 3.1 Cloud Storageモジュールのディレクトリを作成する
  - `infrastructure/terraform/modules/cloud-storage/`ディレクトリを作成
  - `main.tf`, `variables.tf`, `outputs.tf`を作成

- [x] 3.2 開発環境用Cloud Storageバケットを実装する
  - modules/cloud-storage/main.tfに開発者個人用バケットリソースを追加
  - count = var.environment == "development" ? 1 : 0で条件分岐
  - バケット名に開発者IDを含める（var.developer_id）
  - versioning enabledを設定
  - lifecycle_rule（age = 30日で削除）を設定
  - uniform_bucket_level_access = trueを設定
  - CORS設定（origin: localhost:3000）を追加
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [x] 3.3 本番環境用Cloud Storageバケットを実装する
  - modules/cloud-storage/main.tfにアップロードファイル用バケットリソースを追加
  - count = var.environment == "production" ? 1 : 0で条件分岐
  - lifecycle_rule（age = 365日で削除）を設定
  - uniform_bucket_level_access = trueを設定
  - CORS設定（origin: 本番ドメイン）を追加
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 3.4 Cloud Storageモジュールをmain.tfから呼び出す
  - infrastructure/terraform/main.tfにmodule "cloud_storage"を追加
  - 必要な変数を渡す
  - **Validates: Requirements 2.1, 6.1**


## 4. Artifact Registryモジュールの実装

- [ ] 4.1 Artifact Registryモジュールのディレクトリを作成する
  - `infrastructure/terraform/modules/artifact-registry/`ディレクトリを作成
  - `main.tf`, `variables.tf`, `outputs.tf`を作成

- [ ] 4.2 Artifact Registryリポジトリを実装する
  - modules/artifact-registry/main.tfにリポジトリリソースを追加
  - count = var.environment == "production" ? 1 : 0で条件分岐
  - format = "DOCKER"を設定
  - location = "asia-northeast1"を設定
  - docker_config blockで脆弱性スキャン設定を追加
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**

- [ ] 4.3 Artifact Registryモジュールをmain.tfから呼び出す
  - infrastructure/terraform/main.tfにmodule "artifact_registry"を追加
  - 必要な変数を渡す
  - **Validates: Requirements 8.1**


## 5. Secret Managerモジュールの実装

- [ ] 5.1 Secret Managerモジュールのディレクトリを作成する
  - `infrastructure/terraform/modules/secret-manager/`ディレクトリを作成
  - `main.tf`, `variables.tf`, `outputs.tf`を作成

- [ ] 5.2 データベースパスワード用シークレットを実装する
  - modules/secret-manager/main.tfにrandom_passwordリソースを追加（length = 32）
  - google_secret_manager_secretリソースを追加（count条件付き）
  - google_secret_manager_secret_versionリソースを追加
  - replication { auto {} }を設定
  - **Validates: Requirements 9.1, 9.2, 9.4**

- [ ] 5.3 Secret Managerモジュールをmain.tfから呼び出す
  - infrastructure/terraform/main.tfにmodule "secret_manager"を追加
  - 必要な変数を渡す
  - **Validates: Requirements 9.1**


## 6. Cloud SQLモジュールの実装

- [ ] 6.1 Cloud SQLモジュールのディレクトリを作成する
  - `infrastructure/terraform/modules/cloud-sql/`ディレクトリを作成
  - `main.tf`, `variables.tf`, `outputs.tf`を作成

- [ ] 6.2 Cloud SQLインスタンスを実装する
  - modules/cloud-sql/main.tfにgoogle_sql_database_instanceリソースを追加
  - count = var.environment == "production" ? 1 : 0で条件分岐
  - database_version = "POSTGRES_16"を設定
  - settings.tier = "db-f1-micro"を設定
  - ip_configuration { ipv4_enabled = true, authorized_networks { value = "0.0.0.0/0" }, require_ssl = true }を設定
  - disk_type = "PD_SSD", disk_size = 10を設定
  - maintenance_windowを設定
  - deletion_protection = trueを設定
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6**

- [ ] 6.3 Cloud SQLデータベースとユーザーを実装する
  - google_sql_databaseリソースを追加（name = "travel_agent"）
  - google_sql_userリソースを追加（passwordはvar.db_passwordから取得）
  - **Validates: Requirements 5.7, 5.8**

- [ ] 6.4 Cloud SQLモジュールをmain.tfから呼び出す
  - infrastructure/terraform/main.tfにmodule "cloud_sql"を追加
  - Secret Managerモジュールからdb_passwordを渡す
  - **Validates: Requirements 5.1**


## 7. IAMモジュールの実装

- [ ] 7.1 IAMモジュールのディレクトリを作成する
  - `infrastructure/terraform/modules/iam/`ディレクトリを作成
  - `main.tf`, `variables.tf`, `outputs.tf`を作成

- [ ] 7.2 バックエンド用サービスアカウントを実装する
  - modules/iam/main.tfにgoogle_service_accountリソースを追加（backend-service）
  - count = var.environment == "production" ? 1 : 0で条件分岐
  - google_project_iam_memberでroles/cloudsql.clientを付与
  - google_storage_bucket_iam_memberでroles/storage.objectAdminを付与
  - google_secret_manager_secret_iam_memberでroles/secretmanager.secretAccessorを付与
  - google_project_iam_memberでroles/aiplatform.userを付与
  - **Validates: Requirements 10.1, 10.2, 10.3**

- [ ] 7.3 GitHub Actions用サービスアカウントを実装する
  - google_service_accountリソースを追加（github-actions）
  - google_service_account_iam_memberでWorkload Identity設定
  - google_project_iam_memberでroles/run.adminを付与
  - google_artifact_registry_repository_iam_memberでroles/artifactregistry.writerを付与
  - **Validates: Requirements 10.4, 13.6**

- [ ] 7.4 Firebase Hosting用サービスアカウントを実装する
  - google_service_accountリソースを追加（firebase-deployer）
  - google_project_iam_memberでroles/firebasehosting.adminを付与
  - **Validates: Requirements 10.5**

- [ ] 7.5 IAMモジュールをmain.tfから呼び出す
  - infrastructure/terraform/main.tfにmodule "iam"を追加
  - 必要な変数とモジュール間の依存関係を設定
  - **Validates: Requirements 10.1**


## 8. Cloud Runモジュールの実装

- [ ] 8.1 Cloud Runモジュールのディレクトリを作成する
  - `infrastructure/terraform/modules/cloud-run/`ディレクトリを作成
  - `main.tf`, `variables.tf`, `outputs.tf`を作成

- [ ] 8.2 Cloud Runサービスを実装する
  - modules/cloud-run/main.tfにgoogle_cloud_run_serviceリソースを追加
  - count = var.environment == "production" ? 1 : 0で条件分岐
  - imageをArtifact Registryから取得（変数で指定）
  - env blockで環境変数を設定（GOOGLE_CLOUD_PROJECT、GOOGLE_CLOUD_LOCATION、STORAGE_TYPE、GCS_BUCKET_NAME、DATABASE_HOST、DATABASE_NAME、DATABASE_USER）
  - env blockでDATABASE_PASSWORDをSecret Managerからvalue_from.secret_key_refでマウント
  - resources { limits { cpu = "1000m", memory = "512Mi" } }を設定
  - liveness_probe { http_get { path = "/health" } }を設定
  - service_account_nameを設定
  - metadata.annotations { "autoscaling.knative.dev/minScale" = "0", "autoscaling.knative.dev/maxScale" = "100" }を設定
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.6**

- [ ] 8.3 Cloud Runのパブリックアクセスを設定する
  - google_cloud_run_service_iam_memberリソースを追加
  - role = "roles/run.invoker", member = "allUsers"を設定
  - **Validates: Requirements 3.5, 7.3**

- [ ] 8.4 Cloud Runモジュールをmain.tfから呼び出す
  - infrastructure/terraform/main.tfにmodule "cloud_run"を追加
  - 必要な変数とモジュール間の依存関係を設定
  - **Validates: Requirements 3.1**


## 9. Firebase Hostingの設定

- [ ] 9.1 firebase.jsonを作成する
  - `frontend/firebase.json`を作成
  - hosting.public = "out"を設定
  - hosting.rewritesでAPI呼び出しをCloud Runにルーティング（/api/**）
  - hosting.headersでキャッシュヘッダーを設定（画像、JS、CSS）
  - **Validates: Requirements 4.2, 4.4, 4.5, 4.6, 4.7**

- [ ] 9.2 .firebasercを作成する
  - `frontend/.firebaserc`を作成
  - projects.default = プロジェクトIDを設定（プレースホルダー）
  - **Validates: Requirements 4.1**


## 10. ドキュメントの作成

### 10.1 開発環境（個人）セットアップドキュメント

- [x] 10.1.1 開発環境セットアップ手順書を作成する
  - `infrastructure/terraform/docs/setup-development.md`を作成
  - 前提条件（Terraform、gcloud CLI）を記載
  - 開発用GCPプロジェクト作成手順を記載
  - 必要なAPI有効化コマンドを記載（Cloud Storage APIのみ）
  - 開発環境用ステートバケット作成手順を記載
  - Terraform初期化手順を記載
  - developmentワークスペース作成手順を記載
  - 個人用変数ファイル作成手順を記載
  - 開発環境デプロイ手順を記載
  - **Validates: Requirements 14.1, 14.2, 14.3, 14.5**

- [x] 10.1.2 開発環境クイックスタートガイドを作成する
  - `infrastructure/terraform/docs/quickstart-development.md`を作成
  - 最小限の手順で個人用Storageを作成できるガイド
  - コマンドのコピー&ペーストで実行できる形式
  - **Validates: Requirements 14.1**

### 10.2 本番環境セットアップドキュメント

- [ ] 10.2.1 本番環境セットアップ手順書を作成する
  - `infrastructure/terraform/docs/setup-production.md`を作成
  - 前提条件（Terraform、gcloud CLI、権限）を記載
  - 本番用GCPプロジェクト作成手順を記載
  - 全API有効化コマンドを記載
  - 本番環境用ステートバケット作成手順を記載
  - Terraform初期化手順を記載
  - productionワークスペース作成手順を記載
  - 本番用変数ファイル作成手順を記載
  - 本番環境デプロイ手順を記載
  - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5**

### 10.3 共通ドキュメント

- [ ] 10.3.1 デプロイ手順書を作成する
  - `infrastructure/terraform/docs/deployment.md`を作成
  - 開発環境デプロイ手順を記載
  - 本番環境デプロイ手順を記載
  - ロールバック手順を記載
  - **Validates: Requirements 14.5**

- [ ] 10.3.2 トラブルシューティングガイドを作成する
  - `infrastructure/terraform/docs/troubleshooting.md`を作成
  - よくあるエラーと対処方法を記載（プロジェクトID不正、API無効、権限不足、リソース名重複、ステートロック）
  - Cloud Run実行時のエラー対処を記載
  - **Validates: Requirements 14.6, 14.7**

- [ ] 10.3.3 セキュリティ免責事項を作成する
  - `infrastructure/terraform/docs/SECURITY.md`を作成
  - 非実装のセキュリティ対策を明記（VPC、ファイアウォール、Cloud Run認証、Cloud Armor、Cloud IAP）
  - 本番運用時の推奨事項を記載
  - **Validates: Requirements 7.4, 7.5**


## 11. GitHub Actionsワークフローの作成

- [ ] 11.1 Terraformデプロイワークフローを作成する
  - `.github/workflows/terraform-deploy.yml`を作成
  - Workload Identity認証を設定（google-github-actions/auth@v2）
  - Terraform init、fmt、validate、plan、applyステップを追加
  - プルリクエスト時はplanのみ実行
  - mainブランチへのプッシュ時はapplyを実行
  - working-directory: infrastructure/terraformを設定
  - **Validates: Requirements 13.1, 13.5, 13.6**

- [ ] 11.2 バックエンドデプロイワークフローを作成する
  - `.github/workflows/backend-deploy.yml`を作成
  - Dockerイメージのビルドステップを追加
  - Artifact Registryへのプッシュステップを追加
  - Cloud Runへのデプロイステップを追加（environment: productionで手動承認）
  - **Validates: Requirements 13.2, 13.4**

- [ ] 11.3 フロントエンドデプロイワークフローを作成する
  - `.github/workflows/frontend-deploy.yml`を作成
  - pnpm installステップを追加
  - pnpm run buildステップを追加（Next.js静的ビルド）
  - Firebase Hostingへのデプロイステップを追加
  - **Validates: Requirements 13.3**


## 12. 最終確認とドキュメント更新

- [ ] 12.1 READMEを作成する
  - `infrastructure/terraform/README.md`を作成
  - プロジェクト概要を記載
  - 前提条件を記載
  - クイックスタートガイドを記載
  - ディレクトリ構造を記載
  - ドキュメントへのリンクを記載（setup.md、deployment.md、troubleshooting.md、SECURITY.md）
  - **Validates: Requirements 14.1**

- [ ] 12.2 最終レビューとクリーンアップ
  - 全てのTerraformファイルをレビュー
  - terraform fmtを実行してコードフォーマットを統一
  - terraform validateを実行して構文エラーを確認
  - 不要なコメントやデバッグコードを削除
  - **Validates: All Requirements**
