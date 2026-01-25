# 要件定義書

## はじめに

本ドキュメントは、Google Cloud Platform（GCP）上に構築する歴史学習特化型旅行AIエージェントのインフラストラクチャ要件を定義します。Terraformを使用してInfrastructure as Code（IaC）を実現し、開発環境（個人）と本番環境の2つの環境を管理します。コスト最適化を重視し、必要最小限のリソース構成とします。

## 用語集

- **Terraform**: HashiCorpが開発したインフラストラクチャをコードで管理するツール
- **Backend_Service**: FastAPIで実装されたバックエンドアプリケーション
- **Frontend_Service**: Next.js 16で実装されたフロントエンドアプリケーション（静的エクスポート）
- **Cloud_Run**: GCPのサーバーレスコンテナ実行環境（バックエンド用）
- **Firebase_Hosting**: Firebaseの静的サイトホスティングサービス（フロントエンド用）
- **Cloud_SQL**: GCPのマネージドPostgreSQLデータベースサービス
- **Cloud_Storage**: GCPのオブジェクトストレージサービス
- **Artifact_Registry**: GCPのコンテナイメージレジストリ
- **Secret_Manager**: GCPの機密情報管理サービス
- **VPC**: Virtual Private Cloud（仮想プライベートクラウド）
- **Serverless_VPC_Connector**: Cloud RunからVPC内リソースへの接続を可能にするコネクタ
- **Development_Environment**: 開発者個人のローカル開発環境（Cloud Storageバケットのみクラウド）
- **Production_Environment**: 本番環境（全リソースをGCP上に構築）
- **Workspace**: Terraformの環境分離機能（development/production）
- **GitHub_Actions**: GitHubが提供するCI/CDプラットフォーム
- **Workload_Identity_Federation**: GCPのサービスアカウントキーを使わずに外部IDプロバイダーから認証する仕組み

## 要件

### 要件1: 環境分離とTerraform Workspace管理

**ユーザーストーリー:** インフラ管理者として、開発・本番の2つの環境を独立して管理したい。そうすることで、環境間の干渉を防ぎ、安全なデプロイが可能になる。

#### 受入基準

1. THE Terraform_Configuration SHALL support two workspaces: development and production
2. WHEN a workspace is selected, THE Terraform_Configuration SHALL apply environment-specific variable values
3. THE Terraform_Configuration SHALL use workspace-specific naming conventions to prevent resource name conflicts
4. WHEN resources are created, THE Terraform_Configuration SHALL tag them with the environment name for identification

### 要件2: 開発環境（個人）のCloud Storageバケット管理

**ユーザーストーリー:** 開発者として、個人用のCloud Storageバケットを簡単に作成・削除したい。そうすることで、ローカル開発時にクラウドストレージ機能をテストできる。

#### 受入基準

1. WHEN development workspace is active, THE Terraform_Configuration SHALL create a Cloud Storage bucket for the developer
2. THE Development_Storage_Bucket SHALL use a naming pattern that includes the developer's identifier to ensure uniqueness
3. THE Development_Storage_Bucket SHALL enable versioning for data protection
4. THE Development_Storage_Bucket SHALL configure lifecycle rules to automatically delete old objects after 30 days
5. THE Development_Storage_Bucket SHALL set uniform bucket-level access for simplified permission management
6. WHEN the bucket is destroyed, THE Terraform_Configuration SHALL prevent accidental deletion by requiring explicit confirmation

### 要件3: 本番環境のCloud Run構成（バックエンド）

**ユーザーストーリー:** インフラ管理者として、バックエンドAPIをCloud Runにデプロイしたい。そうすることで、スケーラブルでコスト効率の良いサーバーレス環境を実現できる。

#### 受入基準

1. WHEN production workspace is active, THE Terraform_Configuration SHALL create a Cloud Run service for Backend_Service
2. THE Backend_Cloud_Run_Service SHALL configure environment variables for database connection and Google Cloud settings
3. THE Backend_Cloud_Run_Service SHALL enable automatic scaling with minimum 0 instances and maximum 100 instances
4. THE Backend_Cloud_Run_Service SHALL configure health check endpoints for service monitoring
5. THE Backend_Cloud_Run_Service SHALL allow unauthenticated access (allUsers) for public API endpoints
6. THE Backend_Cloud_Run_Service SHALL NOT use VPC connector (パブリックインターネット経由でCloud SQLに接続)

### 要件4: 本番環境のFirebase Hosting構成（フロントエンド）

**ユーザーストーリー:** インフラ管理者として、フロントエンドをFirebase Hostingにデプロイしたい。そうすることで、CDNによる高速配信とコスト効率の良い静的サイトホスティングを実現できる。

#### 受入基準

1. WHEN production workspace is active, THE Terraform_Configuration SHALL configure Firebase Hosting for Frontend_Service
2. THE Firebase_Hosting SHALL serve Next.js static export files
3. THE Firebase_Hosting SHALL configure custom domain for production environment
4. THE Firebase_Hosting SHALL enable CDN caching for static assets
5. THE Firebase_Hosting SHALL configure rewrite rules to route API requests to Backend_Cloud_Run_Service
6. THE Firebase_Hosting SHALL enable HTTPS by default with automatic certificate management
7. THE Firebase_Hosting SHALL configure cache headers for optimal performance

### 要件5: Cloud SQLデータベース構成

**ユーザーストーリー:** インフラ管理者として、PostgreSQLデータベースをCloud SQLで管理したい。そうすることで、高可用性とバックアップが自動化されたデータベース環境を構築できる。

#### 受入基準

1. WHEN production workspace is active, THE Terraform_Configuration SHALL create a Cloud SQL PostgreSQL instance
2. THE Cloud_SQL_Instance SHALL use PostgreSQL version 16
3. THE Cloud_SQL_Instance SHALL configure machine type as db-f1-micro for cost optimization
4. THE Cloud_SQL_Instance SHALL configure public IP for database connections (VPCは使用しない)
5. THE Cloud_SQL_Instance SHALL allow connections from 0.0.0.0/0 (全IPアドレスからのアクセスを許可)
6. THE Cloud_SQL_Instance SHALL require SSL for all connections
7. THE Cloud_SQL_Instance SHALL create a database named "travel_agent"
8. THE Cloud_SQL_Instance SHALL create a user with credentials stored in Secret_Manager

### 要件6: Cloud Storageバケット構成（本番）

**ユーザーストーリー:** インフラ管理者として、画像やファイルを保存するCloud Storageバケットを管理したい。そうすることで、ユーザーがアップロードしたコンテンツを安全に保存できる。

#### 受入基準

1. WHEN production workspace is active, THE Terraform_Configuration SHALL create a Cloud Storage bucket for application uploads
2. THE Storage_Bucket SHALL configure lifecycle rules to delete objects after 365 days
3. THE Storage_Bucket SHALL set uniform bucket-level access for simplified permission management
4. THE Storage_Bucket SHALL enable CORS configuration to allow frontend access

### 要件7: セキュリティ対策の意図的な非実装

**ユーザーストーリー:** インフラ管理者として、このプロジェクトがプロトタイプ・学習目的であることを明確にしたい。そうすることで、セキュリティ対策が不十分であることを認識した上で開発を進められる。

**重要な注意事項:** 本プロジェクトは、以下のセキュリティ対策を**意図的に実装していません**。これは、プロトタイプ・学習目的のプロジェクトであり、本番運用を想定していないためです。

#### 非実装のセキュリティ対策

1. **VPCネットワーク**: プライベートネットワークを構築せず、Cloud SQLはパブリックIPで公開
2. **ファイアウォールルール**: 特定のIPアドレスからのアクセス制限なし
3. **Cloud Run認証**: 一般公開（allUsers）でアクセス可能
4. **Cloud Armor**: DDoS攻撃対策なし
5. **Cloud IAP**: Identity-Aware Proxyによるアクセス制御なし
6. **VPN/Cloud Interconnect**: オンプレミスとの専用接続なし

#### 受入基準

1. THE Terraform_Configuration SHALL NOT create VPC networks
2. THE Cloud_SQL_Instance SHALL use public IP address for database connections
3. THE Backend_Cloud_Run_Service SHALL allow unauthenticated access (allUsers)
4. THE Documentation SHALL clearly state that this infrastructure is NOT suitable for production use with sensitive data
5. THE Documentation SHALL include a security disclaimer explaining the risks of the current configuration

### 要件8: Artifact Registry構成

**ユーザーストーリー:** インフラ管理者として、Dockerイメージを管理するレジストリを構築したい。そうすることで、ビルドしたコンテナイメージを安全に保存・デプロイできる。

#### 受入基準

1. WHEN production workspace is active, THE Terraform_Configuration SHALL create an Artifact Registry repository
2. THE Artifact_Registry SHALL use Docker format for container images
3. THE Artifact_Registry SHALL configure location as asia-northeast1
4. THE Artifact_Registry SHALL enable vulnerability scanning for security

### 要件9: Secret Manager構成

**ユーザーストーリー:** インフラ管理者として、データベースパスワードやAPIキーなどの機密情報を安全に管理したい。そうすることで、コードに機密情報をハードコードせずに済む。

#### 受入基準

1. WHEN production workspace is active, THE Terraform_Configuration SHALL create secrets in Secret_Manager
2. THE Secret_Manager SHALL store database password with automatic rotation capability
3. THE Secret_Manager SHALL configure IAM permissions to allow Cloud Run services to access secrets
4. THE Secret_Manager SHALL enable secret versioning for rollback capability

### 要件10: IAMロールと権限管理

**ユーザーストーリー:** インフラ管理者として、各サービスに必要最小限の権限を付与したい。そうすることで、セキュリティリスクを最小化できる。

#### 受入基準

1. THE Terraform_Configuration SHALL create service accounts for Backend_Service
2. THE Backend_Service_Account SHALL have permissions to access Cloud SQL, Cloud Storage, and Secret_Manager
3. THE Service_Accounts SHALL follow the principle of least privilege
4. THE Terraform_Configuration SHALL configure workload identity for secure authentication
5. THE Terraform_Configuration SHALL grant Firebase Hosting necessary permissions to serve static content

### 要件11: Terraformステート管理

**ユーザーストーリー:** インフラ管理者として、Terraformのステートファイルを安全に管理したい。そうすることで、チームメンバー間でインフラ状態を共有し、同時編集の競合を防げる。

#### 受入基準

1. THE Terraform_Configuration SHALL use Cloud Storage backend for state file storage
2. THE Terraform_State_Bucket SHALL enable versioning for state file history
3. THE Terraform_Configuration SHALL enable state locking using Cloud Storage
4. THE Terraform_State_Bucket SHALL configure encryption at rest
5. THE Terraform_State_Bucket SHALL restrict access to infrastructure administrators only

### 要件12: コスト最適化

**ユーザーストーリー:** インフラ管理者として、クラウドコストを最適化したい。そうすることで、予算内で効率的にサービスを運用できる。

#### 受入基準

1. THE Terraform_Configuration SHALL configure Cloud Run services with minimum instances set to 0 for cost savings
2. THE Terraform_Configuration SHALL use Firebase Hosting free tier for frontend hosting to minimize costs
3. THE Terraform_Configuration SHALL use db-f1-micro instance type for Cloud SQL to minimize database costs
4. THE Terraform_Configuration SHALL configure Cloud Storage lifecycle policies to reduce storage costs
5. THE Terraform_Configuration SHALL tag all resources with cost center labels for cost tracking

### 要件13: CI/CDパイプライン統合（GitHub Actions）

**ユーザーストーリー:** 開発者として、コードをプッシュしたら自動的にデプロイされる仕組みが欲しい。そうすることで、手動デプロイの手間とミスを削減できる。

#### 受入基準

1. THE Terraform_Configuration SHALL integrate with GitHub Actions for automated deployments
2. WHEN code is pushed to main branch, THE GitHub_Actions_Workflow SHALL build backend Docker image and push to Artifact_Registry
3. WHEN code is pushed to main branch, THE GitHub_Actions_Workflow SHALL build frontend static files and deploy to Firebase Hosting
4. WHEN backend image is pushed, THE GitHub_Actions_Workflow SHALL deploy to production environment with manual approval
5. THE GitHub_Actions_Workflow SHALL run Terraform plan before apply to show infrastructure changes
6. THE GitHub_Actions_Workflow SHALL use Workload Identity Federation for secure authentication to GCP

### 要件14: ローカルからのインフラ構築手順

**ユーザーストーリー:** インフラ管理者として、ローカル環境からTerraformを実行してインフラを構築したい。そうすることで、初期セットアップや緊急時の手動操作が可能になる。

#### 受入基準

1. THE Terraform_Configuration SHALL provide clear documentation for local execution
2. THE Documentation SHALL include prerequisites (Terraform version, gcloud CLI, required permissions)
3. THE Documentation SHALL include step-by-step instructions for initial setup
4. THE Documentation SHALL include commands for workspace creation and switching
5. THE Documentation SHALL include commands for applying and destroying infrastructure
6. THE Documentation SHALL include troubleshooting guide for common errors
7. THE Terraform_Configuration SHALL support authentication via gcloud CLI for local execution
