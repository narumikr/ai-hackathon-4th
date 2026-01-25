# GCP Terraform Infrastructure

このディレクトリには、GCP上に構築する歴史学習特化型旅行AIエージェントのインフラストラクチャをTerraformで管理するための設定が含まれています。

## 概要

Terraformワークスペースを使用して、開発環境と本番環境を分離します：

- **development**: 開発者個人用環境（Cloud Storageバケットのみ）
- **production**: 本番環境（全リソース）

## 前提条件

- Terraform 1.6.0以上
- Google Cloud SDK (gcloud CLI)
- Google Cloudアカウント

## クイックスタート

### 開発環境（個人用Cloud Storage）

最小限の手順で個人用Cloud Storageバケットを作成する場合：

```bash
# クイックスタートガイドを参照
cat docs/quickstart-development.md
```

詳細な手順は [docs/setup-development.md](./docs/setup-development.md) を参照してください。

### 本番環境

本番環境のセットアップ手順は [docs/setup-production.md](./docs/setup-production.md) を参照してください（未実装）。

## ディレクトリ構造

```
infrastructure/terraform/
├── main.tf                              # メイン設定ファイル
├── variables.tf                         # 変数定義
├── outputs.tf                           # 出力値定義
├── versions.tf                          # Terraformとプロバイダーのバージョン指定
├── backend.tf                           # バックエンド設定（Git管理対象外）
├── backend-development.tf.example       # 開発環境用バックエンド設定テンプレート
├── backend-production.tf.example        # 本番環境用バックエンド設定テンプレート
├── terraform.tfvars.example             # 変数値のサンプル
│
├── modules/                             # Terraformモジュール
│   ├── cloud-storage/                   # Cloud Storageモジュール
│   ├── artifact-registry/               # Artifact Registryモジュール（未実装）
│   ├── secret-manager/                  # Secret Managerモジュール（未実装）
│   ├── cloud-sql/                       # Cloud SQLモジュール（未実装）
│   ├── iam/                             # IAMモジュール（未実装）
│   └── cloud-run/                       # Cloud Runモジュール（未実装）
│
├── environments/                        # 環境ごとの変数ファイル
│   ├── development-template.tfvars      # 開発環境用テンプレート
│   ├── development-*.tfvars             # 個人用開発環境設定（Git管理対象外）
│   └── production.tfvars                # 本番環境用設定
│
└── docs/                                # ドキュメント
    ├── setup-development.md             # 開発環境セットアップ手順
    ├── quickstart-development.md        # 開発環境クイックスタート
    ├── setup-production.md              # 本番環境セットアップ手順（未実装）
    ├── deployment.md                    # デプロイ手順（未実装）
    ├── troubleshooting.md               # トラブルシューティング（未実装）
    └── SECURITY.md                      # セキュリティ免責事項（未実装）
```

## backend.tfの設定

Terraformのステートファイルを保存するバックエンド設定は、環境ごとに異なります。

### 開発環境の場合

```bash
# 開発環境用テンプレートをコピー
cp backend-development.tf.example backend.tf

# プロジェクトIDを置き換え
sed -i.bak "s/YOUR-DEV-PROJECT-ID/実際のプロジェクトID/g" backend.tf
```

### 本番環境の場合

```bash
# 本番環境用テンプレートをコピー
cp backend-production.tf.example backend.tf

# プロジェクトIDを置き換え
sed -i.bak "s/YOUR-PROD-PROJECT-ID/実際のプロジェクトID/g" backend.tf
```

**重要**: `backend.tf` は `.gitignore` に追加されており、Gitにコミットされません。各開発者が自分の環境に合わせて作成する必要があります。

## ワークスペースの使い方

```bash
# ワークスペース一覧を表示
terraform workspace list

# ワークスペースを作成
terraform workspace new development
terraform workspace new production

# ワークスペースを切り替え
terraform workspace select development

# 現在のワークスペースを確認
terraform workspace show
```

## デプロイ

### 開発環境

```bash
# 個人用ワークスペースに切り替え（例: dev-YOUR-NAME）
terraform workspace select dev-YOUR-NAME

# プランを確認
terraform plan -var-file=environments/development-YOUR-NAME.tfvars

# デプロイ
terraform apply -var-file=environments/development-YOUR-NAME.tfvars
```

### 本番環境

```bash
# productionワークスペースに切り替え
terraform workspace select production

# プランを確認
terraform plan -var-file=environments/production.tfvars

# デプロイ
terraform apply -var-file=environments/production.tfvars
```

## セキュリティに関する注意事項

**このインフラストラクチャは、プロトタイプ・学習目的で構築されており、以下のセキュリティ対策が実装されていません：**

- VPCネットワーク
- ファイアウォールルール
- Cloud Run認証
- Cloud Armor（DDoS攻撃対策）
- Cloud IAP（Identity-Aware Proxy）

詳細は [docs/SECURITY.md](./docs/SECURITY.md) を参照してください（未実装）。

## トラブルシューティング

問題が発生した場合は、[docs/troubleshooting.md](./docs/troubleshooting.md) を参照してください（未実装）。

## ドキュメント

- [開発環境セットアップ手順](./docs/setup-development.md)
- [開発環境クイックスタート](./docs/quickstart-development.md)
- [本番環境セットアップ手順](./docs/setup-production.md)（未実装）
- [デプロイ手順](./docs/deployment.md)（未実装）
- [トラブルシューティング](./docs/troubleshooting.md)（未実装）
- [セキュリティ免責事項](./docs/SECURITY.md)（未実装）

## 参考リンク

- [Terraform Documentation](https://developer.hashicorp.com/terraform/docs)
- [Google Cloud Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Storage Documentation](https://cloud.google.com/storage/docs)
