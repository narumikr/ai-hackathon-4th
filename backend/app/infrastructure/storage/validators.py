"""ファイル検証ユーティリティ"""

import filetype

from app.infrastructure.storage.exceptions import (
    FileSizeExceededError,
    UnsupportedImageFormatError,
)

# サポートされている画像形式（filetypeライブラリの拡張子形式）
SUPPORTED_IMAGE_FORMATS = {"jpg", "jpeg", "png", "webp"}

# サポートされているMIMEタイプ
SUPPORTED_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}


def validate_image_format(file_data: bytes, content_type: str) -> None:
    """画像形式を検証する

    MIMEタイプと実際のファイル内容の両方をチェックして、
    サポートされている画像形式かどうかを検証する

    Args:
        file_data: 検証するファイルのバイトデータ
        content_type: ファイルのMIMEタイプ

    Raises:
        UnsupportedImageFormatError: サポートされていない画像形式の場合
    """
    # 早期失敗: MIMEタイプのチェック
    if content_type not in SUPPORTED_MIME_TYPES:
        raise UnsupportedImageFormatError(
            f"サポートされていないMIMEタイプです: {content_type}。"
            f"対応形式: {', '.join(SUPPORTED_MIME_TYPES)}"
        )

    # 早期失敗: 実際のファイル内容のチェック
    # filetype.guess() で実際の画像形式を判定
    kind = filetype.guess(file_data)

    if kind is None:
        raise UnsupportedImageFormatError(
            f"ファイル形式を判定できませんでした。"
            f"対応形式: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        )

    image_format = kind.extension  # 'jpg', 'png', 'webp' など

    if image_format not in SUPPORTED_IMAGE_FORMATS:
        raise UnsupportedImageFormatError(
            f"サポートされていない画像形式です: {image_format}。"
            f"対応形式: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
        )


def validate_file_size(file_data: bytes, max_size: int) -> None:
    """ファイルサイズを検証する

    Args:
        file_data: 検証するファイルのバイトデータ
        max_size: 最大ファイルサイズ（バイト単位）

    Raises:
        FileSizeExceededError: ファイルサイズが上限を超えた場合
    """
    file_size = len(file_data)

    # 早期失敗: サイズ超過チェック
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        actual_size_mb = file_size / (1024 * 1024)
        raise FileSizeExceededError(
            f"ファイルサイズが上限を超えています。"
            f"最大サイズ: {max_size_mb:.1f}MB、実際のサイズ: {actual_size_mb:.1f}MB"
        )


def validate_upload_file(
    file_data: bytes,
    content_type: str,
    max_size: int,
) -> None:
    """アップロードファイルを総合的に検証する

    画像形式とファイルサイズの両方を検証する

    Args:
        file_data: 検証するファイルのバイトデータ
        content_type: ファイルのMIMEタイプ
        max_size: 最大ファイルサイズ（バイト単位）

    Raises:
        UnsupportedImageFormatError: サポートされていない画像形式の場合
        FileSizeExceededError: ファイルサイズが上限を超えた場合
    """
    # 早期失敗: サイズを先にチェック（大きなファイルの場合、形式チェック前に弾く）
    validate_file_size(file_data, max_size)

    # 早期失敗: 画像形式のチェック
    validate_image_format(file_data, content_type)
