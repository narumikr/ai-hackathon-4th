"""ストレージサービスのカスタム例外クラス"""


class StorageError(Exception):
    """ストレージサービスの基底例外クラス

    すべてのストレージ関連の例外の基底クラス
    """

    pass


class UnsupportedImageFormatError(StorageError):
    """サポートされていない画像形式エラー

    JPEG, PNG, WebP以外の形式のファイルがアップロードされた場合に発生する例外
    """

    pass


class FileSizeExceededError(StorageError):
    """ファイルサイズ超過エラー

    アップロードされたファイルのサイズが上限を超えた場合に発生する例外
    """

    pass


class StorageOperationError(StorageError):
    """ストレージ操作エラー

    ファイルのアップロード、削除、取得などの操作に失敗した場合に発生する例外
    ネットワークエラー、権限エラー、ファイルが存在しないなどが含まれる
    """

    pass
