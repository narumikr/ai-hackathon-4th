"""ローカル開発用ストレージサービス実装"""

from pathlib import Path

import aiofiles

from app.application.ports.storage_service import IStorageService
from app.config.settings import get_settings
from app.infrastructure.storage.exceptions import StorageOperationError
from app.infrastructure.storage.validators import validate_upload_file


class LocalStorageService(IStorageService):
    """ローカル開発用ストレージサービス

    ./uploads/ ディレクトリにファイルを保存する
    ディレクトリ構造: uploads/travels/{travel_id}/ または uploads/reflections/{reflection_id}/
    """

    def __init__(self, upload_dir: str, base_url: str = "http://localhost:8000") -> None:
        """LocalStorageServiceを初期化する

        Args:
            upload_dir: アップロードディレクトリのパス（例: "./uploads"）
            base_url: ベースURL（デフォルト: "http://localhost:8000"）
        """
        self.upload_dir = Path(upload_dir).resolve()
        self.base_url = base_url.rstrip("/")

        # アップロードディレクトリを作成（存在しない場合）
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _validate_path(self, destination: str) -> Path:
        """パスを正規化し、upload_dir配下であることを検証する

        Args:
            destination: ファイルの相対パス

        Returns:
            Path: 検証済みの絶対パス

        Raises:
            StorageOperationError: パストラバーサル攻撃など不正なパスの場合
        """
        # 相対パスを解決
        file_path = (self.upload_dir / destination).resolve()

        # upload_dir配下かチェック（パストラバーサル対策）
        try:
            file_path.relative_to(self.upload_dir)
        except ValueError as e:
            raise StorageOperationError(
                f"不正なファイルパスです: {destination}。upload_dir外へのアクセスは許可されていません。"
            ) from e

        return file_path

    async def upload_file(
        self,
        file_data: bytes,
        destination: str,
        content_type: str,
    ) -> str:
        """ファイルをローカルディレクトリにアップロードする

        Args:
            file_data: アップロードするファイルのバイトデータ
            destination: 保存先のパス（例: "travels/123/image.jpg"）
            content_type: ファイルのMIMEタイプ

        Returns:
            str: アップロードされたファイルのURL

        Raises:
            UnsupportedImageFormatError: サポートされていない画像形式
            FileSizeExceededError: ファイルサイズ超過
            StorageOperationError: ファイル保存失敗
        """
        # ファイル検証（サイズ・形式チェック）
        settings = get_settings()
        validate_upload_file(file_data, content_type, settings.max_upload_size)

        try:
            # パストラバーサル対策：パスを検証
            file_path = self._validate_path(destination)

            # 親ディレクトリを作成（存在しない場合）
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # ファイルを非同期で保存
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_data)

            # URLを生成して返す
            return f"{self.base_url}/uploads/{destination}"

        except StorageOperationError:
            # 既に処理済みのエラーはそのまま再発生
            raise

        except Exception as e:
            raise StorageOperationError(
                f"ファイルの保存に失敗しました: {destination}。エラー: {e}"
            ) from e

    async def get_file_url(self, file_path: str) -> str:
        """ファイルのURLを取得する

        Args:
            file_path: ファイルのパス

        Returns:
            str: ファイルのURL

        Raises:
            StorageOperationError: ファイルが存在しない
        """
        # パストラバーサル対策：パスを検証
        full_path = self._validate_path(file_path)

        # 早期失敗: ファイル存在チェック
        if not full_path.exists():
            raise StorageOperationError(f"ファイルが存在しません: {file_path}")

        return f"{self.base_url}/uploads/{file_path}"

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
            # パストラバーサル対策：パスを検証
            full_path = self._validate_path(file_path)

            # ファイルが存在しない場合はFalseを返す
            if not full_path.exists():
                return False

            # ファイルを削除
            full_path.unlink()
            return True

        except StorageOperationError:
            # 既に処理済みのエラーはそのまま再発生
            raise

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
            # パストラバーサル対策：パスを検証
            full_path = self._validate_path(file_path)
            return full_path.exists() and full_path.is_file()

        except StorageOperationError:
            # 既に処理済みのエラーはそのまま再発生
            raise

        except Exception as e:
            raise StorageOperationError(
                f"ファイルの存在確認に失敗しました: {file_path}。エラー: {e}"
            ) from e
