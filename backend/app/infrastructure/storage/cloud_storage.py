"""Google Cloud Storage統合実装"""

import asyncio
from datetime import timedelta

import google.auth
from google.api_core import exceptions as google_exceptions
from google.auth.transport.requests import Request
from google.cloud import storage
from google.cloud.storage import Blob, Bucket

from app.application.ports.storage_service import IStorageService
from app.config.settings import get_settings
from app.infrastructure.storage.exceptions import StorageOperationError
from app.infrastructure.storage.validators import validate_upload_file


class CloudStorageService(IStorageService):
    """Google Cloud Storage統合サービス

    本番環境でGCSバケットにファイルを保存する
    """

    _CLOUD_PLATFORM_SCOPE = "https://www.googleapis.com/auth/cloud-platform"

    def __init__(
        self,
        bucket_name: str,
        project_id: str | None = None,
        max_retries: int = 3,
        signing_service_account_email: str | None = None,
    ) -> None:
        """CloudStorageServiceを初期化する

        Args:
            bucket_name: GCSバケット名（例: "my-project-travel-uploads"）
            project_id: Google CloudプロジェクトID（Noneの場合はADCから自動取得）
            max_retries: 最大リトライ回数（デフォルト: 3）
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.max_retries = max_retries
        self.signing_service_account_email = (
            signing_service_account_email.strip() if signing_service_account_email else None
        )

        # GCSクライアントの初期化
        # Cloud Run上でIAM SignBlobを利用するため、cloud-platformスコープ付き認証を優先する。
        self.client = self._create_storage_client(project_id)
        self.bucket: Bucket = self.client.bucket(bucket_name)

    async def upload_file(
        self,
        file_data: bytes,
        destination: str,
        content_type: str,
    ) -> str:
        """ファイルをGCSにアップロードする

        Args:
            file_data: アップロードするファイルのバイトデータ
            destination: 保存先のパス（例: "travels/123/image.jpg"）
            content_type: ファイルのMIMEタイプ

        Returns:
            str: アップロードされたファイルの署名付きURL（7日間有効）

        Raises:
            UnsupportedImageFormatError: サポートされていない画像形式
            FileSizeExceededError: ファイルサイズ超過
            StorageOperationError: アップロード失敗
        """
        # ファイル検証（サイズ・形式チェック）
        settings = get_settings()
        validate_upload_file(file_data, content_type, settings.max_upload_size)

        for attempt in range(self.max_retries):
            try:
                # Blobオブジェクトを作成
                blob: Blob = self.bucket.blob(destination)

                # 非同期でアップロード（ブロッキングI/Oを別スレッドで実行）
                await asyncio.to_thread(
                    blob.upload_from_string,
                    file_data,
                    content_type=content_type,
                )

                # 署名付きURL（7日間有効）を生成して返す
                signed_url = await asyncio.to_thread(self._generate_signed_get_url, blob)
                return signed_url

            except google_exceptions.BadRequest as e:
                # 不正なリクエスト（4xx） - リトライしない
                raise StorageOperationError(
                    f"不正なリクエストです: {destination}。エラー: {e}"
                ) from e

            except google_exceptions.Forbidden as e:
                # 権限エラー（403） - リトライしない
                raise StorageOperationError(
                    f"アクセス権限がありません: {destination}。エラー: {e}"
                ) from e

            except google_exceptions.ResourceExhausted as e:
                # クォータ超過エラー（429） - リトライ
                if attempt == self.max_retries - 1:
                    raise StorageOperationError(
                        f"GCSクォータを超過しました: {destination}。エラー: {e}"
                    ) from e
                await self._exponential_backoff(attempt)

            except google_exceptions.ServiceUnavailable as e:
                # サービス利用不可エラー（500系） - リトライ
                if attempt == self.max_retries - 1:
                    raise StorageOperationError(
                        f"GCSサービスが利用できません: {destination}。エラー: {e}"
                    ) from e
                await self._exponential_backoff(attempt)

            except google_exceptions.GoogleAPIError as e:
                # その他のGoogleAPIエラー（5xx系） - リトライ
                if attempt == self.max_retries - 1:
                    raise StorageOperationError(
                        f"GCSへのアップロードに失敗しました: {destination}。エラー: {e}"
                    ) from e
                await self._exponential_backoff(attempt)

            except Exception as e:
                # その他の予期しないエラー - リトライしない
                raise StorageOperationError(
                    f"ファイルのアップロードに失敗しました: {destination}。エラー: {e}"
                ) from e

        # ここには到達しないはずだが、念のため
        raise StorageOperationError(f"最大リトライ回数を超えました: {destination}")

    async def get_file_url(self, file_path: str) -> str:
        """ファイルの署名付きURLを取得する

        Args:
            file_path: ファイルのパス

        Returns:
            str: ファイルの署名付きURL（7日間有効）

        Raises:
            StorageOperationError: ファイルが存在しない、またはURL取得失敗
        """
        try:
            blob: Blob = self.bucket.blob(file_path)

            # ファイルの存在確認（非同期）
            exists = await asyncio.to_thread(blob.exists)

            # 早期失敗: ファイル存在チェック
            if not exists:
                raise StorageOperationError(f"ファイルが存在しません: {file_path}")

            # 署名付きURL（7日間有効）を生成して返す
            signed_url = await asyncio.to_thread(self._generate_signed_get_url, blob)
            return signed_url

        except StorageOperationError:
            # 既に処理済みのエラーはそのまま再発生
            raise

        except Exception as e:
            raise StorageOperationError(
                f"ファイルURLの取得に失敗しました: {file_path}。エラー: {e}"
            ) from e

    async def delete_file(self, file_path: str) -> bool:
        """ファイルを削除する

        Args:
            file_path: 削除するファイルのパス

        Returns:
            bool: 削除成功時True、ファイルが存在しない場合False

        Raises:
            StorageOperationError: 削除操作失敗
        """
        try:
            blob: Blob = self.bucket.blob(file_path)

            # ファイルの存在確認（非同期）
            exists = await asyncio.to_thread(blob.exists)

            if not exists:
                return False

            # ファイルを削除（非同期）
            await asyncio.to_thread(blob.delete)
            return True

        except Exception as e:
            raise StorageOperationError(
                f"ファイルの削除に失敗しました: {file_path}。エラー: {e}"
            ) from e

    async def file_exists(self, file_path: str) -> bool:
        """ファイルが存在するか確認する

        Args:
            file_path: 確認するファイルのパス

        Returns:
            bool: ファイルが存在する場合True、存在しない場合False

        Raises:
            StorageOperationError: 存在確認操作失敗
        """
        try:
            blob: Blob = self.bucket.blob(file_path)
            return await asyncio.to_thread(blob.exists)

        except Exception as e:
            raise StorageOperationError(
                f"ファイルの存在確認に失敗しました: {file_path}。エラー: {e}"
            ) from e

    async def _exponential_backoff(self, attempt: int) -> None:
        """指数バックオフを実行する

        Args:
            attempt: 現在の試行回数（0から開始）
        """
        wait_time = min(2**attempt, 8)  # 最大8秒
        await asyncio.sleep(wait_time)

    def _create_storage_client(self, project_id: str | None) -> storage.Client:
        """storage.Clientを生成する。"""
        try:
            credentials, detected_project_id = google.auth.default(
                scopes=[self._CLOUD_PLATFORM_SCOPE]
            )
            return storage.Client(
                project=project_id or detected_project_id,
                credentials=credentials,
            )
        except Exception:
            # 認証情報の明示取得に失敗した場合は従来の初期化へフォールバックする。
            return storage.Client(project=project_id)

    def _get_signing_service_account_and_token(self) -> tuple[str, str] | None:
        """署名用のservice_account_emailとaccess_tokenを取得する。"""
        credentials_candidates = []

        client_credentials = getattr(self.client, "_credentials", None)
        if client_credentials is not None:
            credentials_candidates.append(client_credentials)

        try:
            default_credentials, _ = google.auth.default(scopes=[self._CLOUD_PLATFORM_SCOPE])
            credentials_candidates.append(default_credentials)
        except Exception:
            pass

        for credentials in credentials_candidates:
            scoped_credentials = credentials

            has_scopes = getattr(scoped_credentials, "has_scopes", None)
            needs_scope = getattr(scoped_credentials, "requires_scopes", False)
            if callable(has_scopes):
                try:
                    needs_scope = not has_scopes([self._CLOUD_PLATFORM_SCOPE])
                except Exception:
                    pass

            if needs_scope and hasattr(scoped_credentials, "with_scopes"):
                scoped_credentials = scoped_credentials.with_scopes([self._CLOUD_PLATFORM_SCOPE])

            if not getattr(scoped_credentials, "token", None):
                scoped_credentials.refresh(Request())

            service_account_email = getattr(scoped_credentials, "service_account_email", None)
            if not service_account_email or service_account_email == "default":
                service_account_email = self.signing_service_account_email

            access_token = getattr(scoped_credentials, "token", None)
            if service_account_email and access_token:
                return service_account_email, access_token

        return None

    def _generate_signed_get_url(self, blob: Blob) -> str:
        """署名付きGET URLを生成する.

        Cloud RunのADC（秘密鍵なし）では通常のgenerate_signed_urlが失敗するため、
        service_account_email + access_token 方式での再試行を行う。
        """
        try:
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET",
            )
        except Exception as e:
            message = str(e)
            if "private key to sign credentials" not in message:
                raise

            signing_credentials = self._get_signing_service_account_and_token()
            if signing_credentials is None:
                raise
            service_account_email, access_token = signing_credentials

            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET",
                service_account_email=service_account_email,
                access_token=access_token,
            )
