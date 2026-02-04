# 要件定義書

## はじめに

旅行ガイドアプリケーションに、Gemini (Vertex AI Image Generation API) を使用したスポット画像生成機能を追加します。この機能は、旅行計画の各スポットに対して、そのスポットの特徴を踏まえた画像を自動生成し、ユーザーに視覚的な情報を提供します。画像生成は旅行ガイド生成APIに統合され、スポット毎に並列で実行されることでパフォーマンスを最適化します。

## 用語集

- **System**: 旅行ガイドアプリケーションのバックエンドシステム
- **Image_Generator**: Vertex AI Image Generation APIを使用して画像を生成するコンポーネント
- **Prompt_Builder**: スポット情報から画像生成用プロンプトを構築するコンポーネント
- **Travel_Guide_API**: 旅行ガイドを生成するAPIエンドポイント
- **Spot**: 旅行計画に含まれる観光スポット
- **Image_URL**: 生成された画像のCloud Storage上のURL
- **Parallel_Executor**: 複数のスポットに対して並列で画像生成を実行するコンポーネント

## 要件

### 要件1: 画像生成プロンプトの構築

**ユーザーストーリー:** 開発者として、スポット情報からGeminiを使用して画像生成プロンプトを構築したい。そうすることで、生成される画像が各スポットの特徴を正確に表現できるようにする。

#### 受入基準

1. WHEN スポット情報が提供された場合、THE Prompt_Builder SHALL Gemini APIを呼び出してプロンプトを生成する
2. WHEN Geminiにスポット名と歴史的背景を渡す場合、THE Prompt_Builder SHALL それらの情報を含むプロンプトテンプレートを使用する
3. WHEN Geminiがプロンプトを返した場合、THE Prompt_Builder SHALL そのプロンプトを画像生成用に返す
4. THE Prompt_Builder SHALL Geminiに日本語で画像生成プロンプトを作成するよう指示する
5. THE Prompt_Builder SHALL Geminiにリアルな写真スタイルを指定するプロンプトを作成するよう指示する

### 要件2: 画像生成の実行

**ユーザーストーリー:** 開発者として、Vertex AI Image Generation APIを使用してリアルな写真風の画像を生成したい。そうすることで、各スポットに現実的な視覚的表現を持たせることができる。

#### 受入基準

1. WHEN 有効なプロンプトが提供された場合、THE Image_Generator SHALL Vertex AI Image Generation APIを呼び出す
2. WHEN API呼び出しが成功した場合、THE Image_Generator SHALL 生成された画像データを返す
3. IF API呼び出しが失敗した場合、THEN THE Image_Generator SHALL 適切なエラーを発生させる
4. THE Image_Generator SHALL API呼び出しにasia-northeast1リージョンを使用する
5. THE Image_Generator SHALL 可能な限り現実的でフォトリアリスティックな画像を生成するようパラメータを設定する

### 要件3: 生成画像の保存

**ユーザーストーリー:** 開発者として、生成された画像をCloud Storageに保存したい。そうすることで、フロントエンドアプリケーションからアクセスできるようにする。

#### 受入基準

1. WHEN 画像が生成された場合、THE System SHALL Cloud Storageにアップロードする
2. WHEN アップロードが成功した場合、THE System SHALL アップロードされた画像のURLを返す
3. THE System SHALL 構造化されたディレクトリパスで画像を整理する（例: travel-guides/{plan_id}/spots/{spot_name_urlencoded}.jpg）
4. IF アップロードが失敗した場合、THEN THE System SHALL 適切なエラーを発生させる
5. THE System SHALL アップロードされた画像に適切なコンテンツタイプを設定する

### 要件4: 旅行ガイドAPIへの統合

**ユーザーストーリー:** 開発者として、画像生成を旅行ガイド生成とは独立して実行したい。そうすることで、ガイド生成を待たずに画像を段階的に表示できるようにする。

#### 受入基準

1. WHEN Travel_Guide_APIが旅行ガイドを生成する場合、THE System SHALL 画像生成を非同期で開始する
2. WHEN 画像生成が完了した場合、THE System SHALL 各スポットの画像URLを個別に保存する
3. THE System SHALL 画像生成が完了していないスポットに対して生成中ステータスを返す
4. THE System SHALL 画像生成が失敗したスポットに対して失敗ステータスを返す
5. THE System SHALL 旅行ガイド生成の完了を画像生成の完了を待たずに返す

### 要件5: 画像生成ステータスの管理

**ユーザーストーリー:** 開発者として、各スポットの画像生成ステータスを管理したい。そうすることで、フロントエンドで適切な表示を行えるようにする。

#### 受入基準

1. THE System SHALL 各スポットに画像生成ステータス（未開始、生成中、成功、失敗）を保持する
2. WHEN 画像生成を開始した場合、THE System SHALL ステータスを生成中に更新する
3. WHEN 画像生成が成功した場合、THE System SHALL ステータスを成功に更新し、画像URLを保存する
4. WHEN 画像生成が失敗した場合、THE System SHALL ステータスを失敗に更新する
5. THE System SHALL APIレスポンスに各スポットの画像生成ステータスを含める

### 要件6: 並列処理の実装

**ユーザーストーリー:** 開発者として、複数のスポットに対して画像生成を並列で実行したい。そうすることで、全体の処理時間を最小化する。

#### 受入基準

1. WHEN 複数のスポットが画像生成を必要とする場合、THE Parallel_Executor SHALL それらを並行して実行する
2. THE Parallel_Executor SHALL 並行実行にasyncioを使用する
3. WHEN すべての並列タスクが完了した場合、THE Parallel_Executor SHALL すべての結果を返す
4. IF 一部のタスクが失敗した場合、THE Parallel_Executor SHALL 成功した結果を返す
5. THE Parallel_Executor SHALL リソース枯渇を防ぐために並行実行数を制限する

### 要件7: エラーハンドリング

**ユーザーストーリー:** 開発者として、画像生成の堅牢なエラーハンドリングを実装したい。そうすることで、失敗が適切にログに記録され、アプリケーションを壊さないようにする。

#### 受入基準

1. WHEN Vertex AI APIがエラーを返した場合、THE System SHALL 適切なコンテキストとともにエラーをログに記録する
2. WHEN Cloud Storageアップロードが失敗した場合、THE System SHALL 適切なコンテキストとともにエラーをログに記録する
3. IF レート制限を超えた場合、THEN THE System SHALL 指数バックオフリトライを実装する
4. THE System SHALL リトライ可能なエラーとリトライ不可能なエラーを区別する
5. WHEN エラーが発生した場合、THE System SHALL エラーログにスポット情報を含める

### 要件8: レスポンススキーマの拡張

**ユーザーストーリー:** フロントエンド開発者として、スポット詳細に画像URLと生成ステータスを含めたい。そうすることで、スポット情報と一緒に画像を表示し、生成中の状態を表示できるようにする。

#### 受入基準

1. WHEN 旅行ガイドが返される場合、THE System SHALL 各スポット詳細にimageUrlフィールドとimageStatusフィールドを含める
2. WHEN 画像生成が成功した場合、THE imageUrlフィールド SHALL Cloud Storage URLを含み、imageStatus SHALL "succeeded"である
3. WHEN 画像生成が進行中の場合、THE imageUrlフィールド SHALL nullであり、imageStatus SHALL "processing"である
4. WHEN 画像生成が失敗した場合、THE imageUrlフィールド SHALL nullであり、imageStatus SHALL "failed"である
5. THE System SHALL 既存のAPIコンシューマーとの後方互換性を維持する

### 要件9: 設定管理

**ユーザーストーリー:** システム管理者として、画像生成パラメータを設定したい。そうすることで、画像品質とAPI使用量を制御できるようにする。

#### 受入基準

1. THE System SHALL 環境設定からVertex AIプロジェクトIDを読み取る
2. THE System SHALL 環境設定からCloud Storageバケット名を読み取る
3. THE System SHALL 画像生成モデル名の設定を許可する
4. THE System SHALL 最大同時画像生成数の設定を許可する
5. THE System SHALL すべての設定パラメータに適切なデフォルト値を提供する

### 要件10: フロントエンドでの画像表示

**ユーザーストーリー:** ユーザーとして、スポットカードの左側に生成された画像を表示したい。そうすることで、視覚的にスポット情報を理解できるようにする。

#### 受入基準

1. WHEN ページが読み込まれた時にスポット詳細にimageUrlが含まれる場合、THE System SHALL スポットカードの左側に画像を表示する
2. WHEN ページが読み込まれた時にimageUrlがnullの場合、THE System SHALL デフォルトのプレースホルダー画像を表示する
3. THE System SHALL リアルタイムな画像更新を行わない
4. THE System SHALL 画像のアスペクト比を維持しながら適切なサイズで表示する
5. THE System SHALL 画像に適切なalt属性を設定してアクセシビリティを確保する
