"""CloudStorageServiceのユニットテスト"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.api_core import exceptions as google_exceptions

from app.infrastructure.storage.cloud_storage import CloudStorageService
from app.infrastructure.storage.exceptions import StorageOperationError


@pytest.fixture
def mock_storage_client():
    """GCS Clientのモック"""
    with patch("app.infrastructure.storage.cloud_storage.storage.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        yield mock_client, mock_bucket


@pytest.fixture
def cloud_storage(mock_storage_client):
    """CloudStorageServiceのフィクスチャ"""
    _, _ = mock_storage_client
    return CloudStorageService(
        bucket_name="test-bucket",
        project_id="test-project",
    )


@pytest.mark.asyncio
async def test_upload_file_成功(cloud_storage, mock_storage_client):
    """
    前提条件:
    - CloudStorageServiceが初期化されている
    - GCSクライアントがモック化されている

    検証項目:
    - ファイルが正しくアップロードされる
    - 署名付きURLが返される
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/test-bucket/travels/123/image.jpg?X-Goog-Signature=..."
    mock_bucket.blob.return_value = mock_blob

    # テストデータ（JPEG画像のマジックバイト）
    file_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"a" * 1000
    destination = "travels/123/image.jpg"
    content_type = "image/jpeg"

    # アップロード実行
    url = await cloud_storage.upload_file(file_data, destination, content_type)

    # 検証
    assert url == mock_blob.generate_signed_url.return_value
    mock_bucket.blob.assert_called_once_with(destination)
    mock_blob.upload_from_string.assert_called_once_with(
        file_data,
        content_type=content_type,
    )
    mock_blob.generate_signed_url.assert_called_once()


@pytest.mark.asyncio
async def test_upload_file_リトライ成功(cloud_storage, mock_storage_client):
    """
    前提条件:
    - 最初のアップロードがServiceUnavailableで失敗する
    - 2回目のリトライで成功する

    検証項目:
    - リトライが実行される
    - 最終的にアップロードが成功する
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/test-bucket/travels/123/image.jpg?X-Goog-Signature=..."
    mock_bucket.blob.return_value = mock_blob

    # 1回目は失敗、2回目は成功
    mock_blob.upload_from_string.side_effect = [
        google_exceptions.ServiceUnavailable("Service temporarily unavailable"),
        None,  # 2回目は成功
    ]

    # JPEG画像のマジックバイト
    file_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"a" * 1000
    destination = "travels/123/image.jpg"
    content_type = "image/jpeg"

    # アップロード実行
    url = await cloud_storage.upload_file(file_data, destination, content_type)

    # 検証
    assert url == mock_blob.generate_signed_url.return_value
    assert mock_blob.upload_from_string.call_count == 2


@pytest.mark.asyncio
async def test_upload_file_最大リトライ超過(cloud_storage, mock_storage_client):
    """
    前提条件:
    - すべてのリトライがServiceUnavailableで失敗する

    検証項目:
    - StorageOperationErrorが発生する
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    # すべてのリトライが失敗
    mock_blob.upload_from_string.side_effect = google_exceptions.ServiceUnavailable(
        "Service unavailable"
    )

    # JPEG画像のマジックバイト
    file_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"a" * 1000
    destination = "travels/123/image.jpg"
    content_type = "image/jpeg"

    # アップロード実行（エラー発生を期待）
    with pytest.raises(StorageOperationError, match="GCSサービスが利用できません"):
        await cloud_storage.upload_file(file_data, destination, content_type)

    # 最大リトライ回数（3回）試行されたことを確認
    assert mock_blob.upload_from_string.call_count == 3


@pytest.mark.asyncio
async def test_get_file_url_成功(cloud_storage, mock_storage_client):
    """
    前提条件:
    - ファイルが存在する

    検証項目:
    - 署名付きURLが返される
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/test-bucket/travels/123/image.jpg?X-Goog-Signature=..."
    mock_blob.exists.return_value = True
    mock_bucket.blob.return_value = mock_blob

    file_path = "travels/123/image.jpg"

    # URL取得
    url = await cloud_storage.get_file_url(file_path)

    # 検証
    assert url == mock_blob.generate_signed_url.return_value
    mock_bucket.blob.assert_called_once_with(file_path)
    mock_blob.exists.assert_called_once()
    mock_blob.generate_signed_url.assert_called_once()


@pytest.mark.asyncio
async def test_get_file_url_ファイル不存在エラー(cloud_storage, mock_storage_client):
    """
    前提条件:
    - ファイルが存在しない

    検証項目:
    - StorageOperationErrorが発生する
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket.blob.return_value = mock_blob

    file_path = "travels/999/nonexistent.jpg"

    # URL取得（エラー発生を期待）
    with pytest.raises(StorageOperationError, match="ファイルが存在しません"):
        await cloud_storage.get_file_url(file_path)


@pytest.mark.asyncio
async def test_delete_file_成功(cloud_storage, mock_storage_client):
    """
    前提条件:
    - ファイルが存在する

    検証項目:
    - ファイルが削除される
    - Trueが返される
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_bucket.blob.return_value = mock_blob

    file_path = "travels/123/image.jpg"

    # 削除実行
    result = await cloud_storage.delete_file(file_path)

    # 検証
    assert result is True
    mock_blob.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_file_ファイル不存在(cloud_storage, mock_storage_client):
    """
    前提条件:
    - ファイルが存在しない

    検証項目:
    - Falseが返される
    - deleteは呼ばれない
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket.blob.return_value = mock_blob

    file_path = "travels/999/nonexistent.jpg"

    # 削除実行
    result = await cloud_storage.delete_file(file_path)

    # 検証
    assert result is False
    mock_blob.delete.assert_not_called()


@pytest.mark.asyncio
async def test_file_exists_ファイルが存在する(cloud_storage, mock_storage_client):
    """
    前提条件:
    - ファイルが存在する

    検証項目:
    - Trueが返される
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.exists.return_value = True
    mock_bucket.blob.return_value = mock_blob

    file_path = "travels/123/image.jpg"

    # 存在確認
    result = await cloud_storage.file_exists(file_path)

    # 検証
    assert result is True


@pytest.mark.asyncio
async def test_file_exists_ファイルが存在しない(cloud_storage, mock_storage_client):
    """
    前提条件:
    - ファイルが存在しない

    検証項目:
    - Falseが返される
    """
    _, mock_bucket = mock_storage_client

    # モックのBlob設定
    mock_blob = MagicMock()
    mock_blob.exists.return_value = False
    mock_bucket.blob.return_value = mock_blob

    file_path = "travels/999/nonexistent.jpg"

    # 存在確認
    result = await cloud_storage.file_exists(file_path)

    # 検証
    assert result is False
