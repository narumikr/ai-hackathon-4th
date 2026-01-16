"""ストレージサービスのポートインターフェース"""

from abc import ABC, abstractmethod


class IStorageService(ABC):
    """ストレージサービスのインターフェース

    ドメイン層でのストレージサービスインターフェース定義
    実装はインフラ層で提供される
    """

    @abstractmethod
    async def upload_file(
        self,
        file_data: bytes,
        destination: str,
        content_type: str,
    ) -> str:
        """ファイルをアップロードする

        Args:
            file_data: アップロードするファイルのバイトデータ
            destination: 保存先のパス（例: "travels/123/image.jpg"）
            content_type: ファイルのMIMEタイプ（例: "image/jpeg"）

        Returns:
            str: アップロードされたファイルのURL

        Raises:
            UnsupportedImageFormatError: サポートされていない画像形式
            FileSizeExceededError: ファイルサイズ超過
            StorageOperationError: ストレージ操作失敗
        """
        pass

    @abstractmethod
    async def get_file_url(self, file_path: str) -> str:
        """ファイルのURLを取得する

        Args:
            file_path: ファイルのパス

        Returns:
            str: ファイルのURL

        Raises:
            StorageOperationError: ファイルが存在しない、またはURL取得失敗
        """
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """ファイルを削除する

        Args:
            file_path: 削除するファイルのパス

        Returns:
            bool: 削除成功時True、ファイルが存在しない場合False

        Raises:
            StorageOperationError: 削除操作失敗
        """
        pass

    @abstractmethod
    async def file_exists(self, file_path: str) -> bool:
        """ファイルが存在するか確認する

        Args:
            file_path: 確認するファイルのパス

        Returns:
            bool: ファイルが存在する場合True、存在しない場合False

        Raises:
            StorageOperationError: 存在確認操作失敗
        """
        pass
