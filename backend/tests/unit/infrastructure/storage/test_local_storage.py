"""LocalStorageServiceのユニットテスト"""

import tempfile
from pathlib import Path

import pytest

from app.infrastructure.storage.exceptions import StorageOperationError
from app.infrastructure.storage.local_storage import LocalStorageService


@pytest.fixture
def temp_upload_dir():
    """一時的なアップロードディレクトリを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def local_storage(temp_upload_dir):
    """LocalStorageServiceのフィクスチャ"""
    return LocalStorageService(upload_dir=temp_upload_dir)


@pytest.mark.asyncio
async def test_upload_file_成功(local_storage, temp_upload_dir):
    """
    前提条件:
    - LocalStorageServiceが初期化されている
    - 有効なファイルデータとdestinationが与えられる

    検証項目:
    - ファイルが正しく保存される
    - 正しいURLが返される
    - ファイルが実際に存在する
    """
    # テストデータ（JPEG画像のマジックバイト）
    file_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"a" * 1000
    destination = "travels/123/test-image.jpg"
    content_type = "image/jpeg"

    # アップロード実行
    url = await local_storage.upload_file(file_data, destination, content_type)

    # 検証
    assert url == f"http://localhost:8000/uploads/{destination}"

    # ファイルが実際に保存されていることを確認
    file_path = Path(temp_upload_dir) / destination
    assert file_path.exists()
    assert file_path.read_bytes() == file_data


@pytest.mark.asyncio
async def test_upload_file_親ディレクトリ自動作成(local_storage, temp_upload_dir):
    """
    前提条件:
    - 親ディレクトリが存在しない
    - 深い階層のdestinationが与えられる

    検証項目:
    - 親ディレクトリが自動的に作成される
    - ファイルが正しく保存される
    """
    # PNG画像のマジックバイト
    file_data = b"\x89PNG\r\n\x1a\n" + b"a" * 1000
    destination = "travels/456/sub/dir/image.png"
    content_type = "image/png"

    url = await local_storage.upload_file(file_data, destination, content_type)

    # 親ディレクトリが作成されていることを確認
    file_path = Path(temp_upload_dir) / destination
    assert file_path.parent.exists()
    assert file_path.exists()


@pytest.mark.asyncio
async def test_get_file_url_成功(local_storage, temp_upload_dir):
    """
    前提条件:
    - ファイルが既に存在する

    検証項目:
    - 正しいURLが返される
    """
    # ファイルを事前に作成
    file_path = "travels/789/existing.jpg"
    full_path = Path(temp_upload_dir) / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(b"existing file")

    # URL取得
    url = await local_storage.get_file_url(file_path)

    # 検証
    assert url == f"http://localhost:8000/uploads/{file_path}"


@pytest.mark.asyncio
async def test_get_file_url_ファイル不存在エラー(local_storage):
    """
    前提条件:
    - 指定されたファイルが存在しない

    検証項目:
    - StorageOperationErrorが発生する
    """
    file_path = "travels/999/nonexistent.jpg"

    with pytest.raises(StorageOperationError, match="ファイルが存在しません"):
        await local_storage.get_file_url(file_path)


@pytest.mark.asyncio
async def test_delete_file_成功(local_storage, temp_upload_dir):
    """
    前提条件:
    - ファイルが既に存在する

    検証項目:
    - ファイルが正しく削除される
    - Trueが返される
    """
    # ファイルを事前に作成
    file_path = "travels/111/to-delete.jpg"
    full_path = Path(temp_upload_dir) / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(b"file to delete")

    # 削除実行
    result = await local_storage.delete_file(file_path)

    # 検証
    assert result is True
    assert not full_path.exists()


@pytest.mark.asyncio
async def test_delete_file_ファイル不存在(local_storage):
    """
    前提条件:
    - 指定されたファイルが存在しない

    検証項目:
    - Falseが返される
    - エラーは発生しない
    """
    file_path = "travels/222/nonexistent.jpg"

    result = await local_storage.delete_file(file_path)

    # 検証
    assert result is False


@pytest.mark.asyncio
async def test_file_exists_ファイルが存在する(local_storage, temp_upload_dir):
    """
    前提条件:
    - ファイルが既に存在する

    検証項目:
    - Trueが返される
    """
    # ファイルを事前に作成
    file_path = "travels/333/existing.jpg"
    full_path = Path(temp_upload_dir) / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(b"existing file")

    result = await local_storage.file_exists(file_path)

    # 検証
    assert result is True


@pytest.mark.asyncio
async def test_file_exists_ファイルが存在しない(local_storage):
    """
    前提条件:
    - 指定されたファイルが存在しない

    検証項目:
    - Falseが返される
    """
    file_path = "travels/444/nonexistent.jpg"

    result = await local_storage.file_exists(file_path)

    # 検証
    assert result is False


@pytest.mark.asyncio
async def test_file_exists_ディレクトリの場合(local_storage, temp_upload_dir):
    """
    前提条件:
    - 指定されたパスがディレクトリである

    検証項目:
    - Falseが返される（ディレクトリはファイルではない）
    """
    dir_path = "travels/555"
    full_path = Path(temp_upload_dir) / dir_path
    full_path.mkdir(parents=True, exist_ok=True)

    result = await local_storage.file_exists(dir_path)

    # 検証
    assert result is False


@pytest.mark.asyncio
async def test_upload_file_パストラバーサル攻撃(local_storage):
    """
    前提条件:
    - パストラバーサルを含むdestinationが与えられる

    検証項目:
    - StorageOperationErrorが発生する
    - upload_dir外へのアクセスが防がれる
    """
    # JPEG画像のマジックバイト
    file_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"a" * 1000
    destination = "../../../etc/passwd"
    content_type = "image/jpeg"

    # パストラバーサル攻撃を試みる
    with pytest.raises(StorageOperationError, match="不正なファイルパスです"):
        await local_storage.upload_file(file_data, destination, content_type)


@pytest.mark.asyncio
async def test_upload_file_絶対パス攻撃(local_storage):
    """
    前提条件:
    - 絶対パスが与えられる

    検証項目:
    - StorageOperationErrorが発生する
    - upload_dir外へのアクセスが防がれる
    """
    # JPEG画像のマジックバイト
    file_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"a" * 1000
    destination = "/tmp/malicious.jpg"
    content_type = "image/jpeg"

    # 絶対パス攻撃を試みる
    with pytest.raises(StorageOperationError, match="不正なファイルパスです"):
        await local_storage.upload_file(file_data, destination, content_type)


@pytest.mark.asyncio
async def test_get_file_url_パストラバーサル攻撃(local_storage):
    """
    前提条件:
    - パストラバーサルを含むfile_pathが与えられる

    検証項目:
    - StorageOperationErrorが発生する
    """
    file_path = "../../../etc/passwd"

    with pytest.raises(StorageOperationError, match="不正なファイルパスです"):
        await local_storage.get_file_url(file_path)


@pytest.mark.asyncio
async def test_delete_file_パストラバーサル攻撃(local_storage):
    """
    前提条件:
    - パストラバーサルを含むfile_pathが与えられる

    検証項目:
    - StorageOperationErrorが発生する
    """
    file_path = "../../../etc/passwd"

    with pytest.raises(StorageOperationError, match="不正なファイルパスです"):
        await local_storage.delete_file(file_path)


@pytest.mark.asyncio
async def test_file_exists_パストラバーサル攻撃(local_storage):
    """
    前提条件:
    - パストラバーサルを含むfile_pathが与えられる

    検証項目:
    - StorageOperationErrorが発生する
    """
    file_path = "../../../etc/passwd"

    with pytest.raises(StorageOperationError, match="不正なファイルパスです"):
        await local_storage.file_exists(file_path)
