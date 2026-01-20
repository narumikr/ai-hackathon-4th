# インフラアーキテクチャ図 - Historical Travel Agent

## 概要

このディレクトリには、歴史学習特化型旅行AIエージェントシステムのインフラアーキテクチャ図が含まれています。

## 図表一覧

### 1. システム全体アーキテクチャ
**ファイル**: `system-architecture.drawio`

**内容**:
- GCPサービス全体の構成
- Frontend/Backend/AI/Data/Security/Monitoring の6層構造
- サービス間の接続関係

**主要コンポーネント**:
- Frontend Layer: Firebase Hosting, Cloud CDN
- Backend Layer: Cloud Run, Load Balancing, Cloud Build, Artifact Registry
- AI/ML Layer: Vertex AI (Gemini), Vertex AI Search, Built-in Tools
- Data Layer: Cloud SQL, Memorystore, Cloud Storage
- Security Layer: IAM, Secret Manager, Firebase Auth
- Monitoring Layer: Cloud Monitoring, Cloud Logging, Error Reporting

### 2. ネットワーク構成図
**ファイル**: `network-architecture.drawio`

**内容**:
- VPC、Public/Private サブネット構成
- セキュリティグループの詳細
- Load Balancer、NAT Gateway の配置
- ネットワークフローの可視化

**ネットワーク設計**:
- VPC: `historical-travel-vpc`
- Public Subnet: `10.0.1.0/24`
- Private Subnet: `10.0.2.0/24`
- リージョン: `asia-northeast1` (Tokyo)

### 3. データフロー図
**ファイル**: `data-flow.drawio`

**内容**:
- ユーザー → Frontend → API → 各サービスの流れ
- 7つの主要データフローを色分け表示
- 処理順序と通信プロトコルを明示

**データフロー**:
1. UI Interactions (Travel Plans, Photos)
2. REST API Calls (JSON/FormData)
3. AI Generation (Text + Images)
4. CRUD Operations (SQL Queries)
5. Cache Operations (Session, AI Results)
6. File Operations (Image Upload/Download)
7. Built-in Tools (Search, Maps, Vision)

## Draw.io での使用方法

### 1. オンラインで開く
1. [Draw.io (diagrams.net)](https://app.diagrams.net/) にアクセス
2. "Open Existing Diagram" をクリック
3. "Device" を選択して `.drawio` ファイルをアップロード

### 2. ローカルで編集
1. Draw.io Desktop アプリをダウンロード
2. `.drawio` ファイルを直接開く

### 3. 他の形式でエクスポート
- PNG/JPG: プレゼンテーション用
- SVG: ベクター形式
- PDF: ドキュメント埋め込み用
- XML: バックアップ・共有用

## 図表の更新手順

### 1. 新しいサービス追加時
1. 該当する図表を Draw.io で開く
2. 新しいコンポーネントを追加
3. 接続線を更新
4. レイアウトを調整
5. ファイルを保存

### 2. ネットワーク変更時
1. `network-architecture.drawio` を更新
2. セキュリティグループ設定を反映
3. IP アドレス範囲を確認
4. フロー図も必要に応じて更新

### 3. データフロー変更時
1. `data-flow.drawio` を更新
2. 新しいフローを色分けして追加
3. 凡例を更新
4. 処理順序を確認

## アーキテクチャの特徴

### 高可用性設計
- **Multi-AZ構成**: Cloud SQL の Primary/Replica 構成
- **Auto Scaling**: Cloud Run の自動スケーリング
- **Load Balancing**: Global HTTPS Load Balancer

### セキュリティ設計
- **ネットワーク分離**: Public/Private サブネット分離
- **最小権限原則**: IAM による細かい権限制御
- **暗号化**: 保存時・転送時の暗号化

### パフォーマンス最適化
- **CDN活用**: Firebase Hosting + Cloud CDN
- **キャッシュ戦略**: Redis による多層キャッシュ
- **リージョン最適化**: Asia-Northeast1 (Tokyo) 配置

### コスト最適化
- **サーバーレス**: Cloud Run による従量課金
- **ストレージ階層**: 適切なストレージクラス選択
- **リソース監視**: Cloud Monitoring による使用量監視

## 関連ドキュメント

- [GCPサービス分析](../gcp-services-analysis.md) - 必要なサービスの詳細分析
- [最小構成](../gcp-services-minimal.md) - コスト重視の構成
- [アーキテクチャ設計書](../architecture-design.md) - 詳細な設計仕様

## 更新履歴

| 日付 | 更新者 | 変更内容 |
|------|--------|----------|
| 2024-01-20 | System | 初版作成 |

## 注意事項

- 図表は定期的に実際の構成と同期を取ること
- 新しいサービス追加時は必ず図表を更新すること
- セキュリティに関わる変更は慎重に行うこと
- コスト影響のある変更は事前に見積もりを行うこと