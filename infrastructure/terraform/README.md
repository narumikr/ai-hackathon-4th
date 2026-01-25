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

- [docs/quickstart-development.md](./docs/quickstart-development.md)

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
