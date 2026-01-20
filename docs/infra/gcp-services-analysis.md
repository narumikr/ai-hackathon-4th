# GCPサービス分析 - Historical Travel Agent

## 概要

歴史学習特化型旅行AIエージェントシステムで必要となるGoogle Cloud Platformサービスの詳細分析。

## アプリケーション要件の整理

### 機能要件
1. **旅行前フェーズ**
   - 旅行計画の作成・管理
   - 歴史情報の収集・検索
   - AI による旅行ガイド生成
   - 年表・地図・チェックポイントの生成

2. **旅行後フェーズ**
   - 写真のアップロード・保存
   - AI による画像分析
   - 振り返りパンフレットの生成

3. **共通機能**
   - ユーザー認証・管理
   - データの永続化
   - リアルタイム処理状況の表示

### 技術要件
- **フロントエンド**: Next.js 16 (静的サイト生成)
- **バックエンド**: Python FastAPI (コンテナ化)
- **データベース**: PostgreSQL + Redis
- **AI処理**: Vertex AI Gemini (マルチモーダル)
- **ファイル処理**: 画像アップロード・保存

## 必要なGCPサービス一覧

### 🔴 必須サービス（コア機能）

#### 1. Compute Services
| サービス | 用途 | 理由 |
|---------|------|------|
| **Cloud Run** | バックエンドAPI (FastAPI) | サーバーレス、自動スケーリング、コンテナベース |
| **Firebase Hosting** | フロントエンド (Next.js静的サイト) | 高速CDN、SSL自動、Next.js最適化 |

#### 2. AI/ML Services
| サービス | 用途 | 理由 |
|---------|------|------|
| **Vertex AI** | Gemini API (テキスト・画像生成) | マルチモーダルAI、Built-in Tools対応 |
| **Vertex AI Search** | 歴史情報検索 (オプション) | 専門的な検索機能、Gemini連携 |

#### 3. Storage Services
| サービス | 用途 | 理由 |
|---------|------|------|
| **Cloud Storage** | 画像ファイル保存 | 高可用性、CDN連携、コスト効率 |
| **Cloud SQL (PostgreSQL)** | 構造化データ (旅行計画、ガイド等) | マネージドDB、自動バックアップ |
| **Memorystore (Redis)** | キャッシュ・セッション管理 | 高速アクセス、AI生成結果キャッシュ |

#### 4. Security & Identity
| サービス | 用途 | 理由 |
|---------|------|------|
| **Identity and Access Management (IAM)** | アクセス制御 | サービス間認証、最小権限原則 |
| **Secret Manager** | API キー・DB認証情報管理 | 機密情報の安全な管理 |

#### 5. DevOps & Deployment
| サービス | 用途 | 理由 |
|---------|------|------|
| **Cloud Build** | CI/CD パイプライン | ソースコードからの自動デプロイ |
| **Artifact Registry** | コンテナイメージ管理 | プライベートレジストリ、脆弱性スキャン |

### 🟡 推奨サービス（運用・監視）

#### 6. Monitoring & Logging
| サービス | 用途 | 理由 |
|---------|------|------|
| **Cloud Monitoring** | システム監視・アラート | パフォーマンス監視、SLA管理 |
| **Cloud Logging** | ログ集約・分析 | 統合ログ管理、デバッグ支援 |
| **Error Reporting** | エラー追跡 | 自動エラー検出・通知 |

#### 7. Networking
| サービス | 用途 | 理由 |
|---------|------|------|
| **Cloud CDN** | 静的コンテンツ配信 | 世界規模での高速配信 |
| **Cloud Load Balancing** | 負荷分散 (スケール時) | 高可用性、自動フェイルオーバー |

### 🔵 オプションサービス（拡張機能）

#### 8. Advanced Features
| サービス | 用途 | 理由 |
|---------|------|------|
| **Firebase Authentication** | ユーザー認証 | ソーシャルログイン、簡単統合 |
| **Cloud Tasks** | 非同期処理キュー | AI生成の長時間処理 |
| **Cloud Scheduler** | 定期実行 | データクリーンアップ、レポート生成 |
| **BigQuery** | データ分析 (将来) | ユーザー行動分析、レコメンデーション |

## サービス選定の根拠

### Compute: Cloud Run vs App Engine vs GKE
**選択: Cloud Run**
- ✅ コンテナベースで開発環境と一致
- ✅ 自動スケーリング（0→N）でコスト効率
- ✅ FastAPI との相性が良い
- ✅ 設定がシンプル

### Frontend: Firebase Hosting vs Cloud Storage + CDN
**選択: Firebase Hosting**
- ✅ Next.js 静的エクスポートに最適化
- ✅ 自動SSL、カスタムドメイン対応
- ✅ プレビューデプロイ機能
- ✅ Cloud Run との統合が簡単

### Database: Cloud SQL vs Firestore vs Spanner
**選択: Cloud SQL (PostgreSQL)**
- ✅ 既存のSQLAlchemy コードと互換
- ✅ 複雑なリレーショナルデータに適している
- ✅ ACID特性が重要（旅行計画の整合性）
- ✅ コスト効率（小〜中規模）

### AI: Vertex AI vs OpenAI API
**選択: Vertex AI (Gemini)**
- ✅ Google Cloud ネイティブ統合
- ✅ Built-in Tools (Search, Maps) 利用可能
- ✅ マルチモーダル対応（テキスト + 画像）
- ✅ データ主権・プライバシー

## コスト見積もり（月額・USD）

### 開発・検証段階（〜100ユーザー/月）
| サービス | 想定使用量 | 月額コスト |
|---------|-----------|-----------|
| Cloud Run | 100万リクエスト/月 | $5-10 |
| Firebase Hosting | 10GB転送/月 | $1-2 |
| Cloud SQL (db-f1-micro) | 24時間稼働 | $7-10 |
| Memorystore (1GB) | 基本インスタンス | $25-30 |
| Cloud Storage | 100GB保存 | $2-3 |
| Vertex AI | 1000回生成/月 | $10-20 |
| その他 (監視・ログ等) | - | $5-10 |
| **合計** | - | **$55-85** |

### 本格運用段階（〜1000ユーザー/月）
| サービス | 想定使用量 | 月額コスト |
|---------|-----------|-----------|
| Cloud Run | 1000万リクエスト/月 | $50-80 |
| Firebase Hosting | 100GB転送/月 | $10-15 |
| Cloud SQL (db-n1-standard-1) | HA構成 | $50-70 |
| Memorystore (5GB) | 標準インスタンス | $100-120 |
| Cloud Storage | 1TB保存 | $20-25 |
| Vertex AI | 10000回生成/月 | $100-200 |
| その他 (監視・ログ等) | - | $20-30 |
| **合計** | - | **$350-540** |

## 次のステップ

1. **インフラ設計書の作成**
   - アーキテクチャ図
   - ネットワーク構成
   - セキュリティ設計

2. **Terraform構成の設計**
   - 環境別設定 (dev/prod)
   - モジュール化

3. **CI/CDパイプラインの設計**
   - GitHub Actions + Cloud Build
   - デプロイ戦略

4. **監視・アラート設計**
   - SLI/SLO定義
   - ダッシュボード設計

## 参考リンク

- [Google Cloud Architecture Center](https://cloud.google.com/architecture)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Firebase Hosting Pricing](https://firebase.google.com/pricing)