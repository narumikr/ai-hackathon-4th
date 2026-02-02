"""画像アップロードAPIのユニットテスト"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.interfaces.api.v1.uploads import _ensure_non_empty, _resolve_extension


class TestResolveExtension:
    """_resolve_extension関数のテスト"""

    def test_resolve_extension_from_content_type_jpeg(self) -> None:
        """前提条件: content_typeがimage/jpeg
        実行: _resolve_extension
        検証: 拡張子がjpgになる
        """
        result = _resolve_extension(None, "image/jpeg")
        assert result == "jpg"

    def test_resolve_extension_from_content_type_png(self) -> None:
        """前提条件: content_typeがimage/png
        実行: _resolve_extension
        検証: 拡張子がpngになる
        """
        result = _resolve_extension(None, "image/png")
        assert result == "png"

    def test_resolve_extension_from_content_type_webp(self) -> None:
        """前提条件: content_typeがimage/webp
        実行: _resolve_extension
        検証: 拡張子がwebpになる
        """
        result = _resolve_extension(None, "image/webp")
        assert result == "webp"

    def test_resolve_extension_from_filename_jpg(self) -> None:
        """前提条件: filenameが.jpg、content_typeがimage/jpeg
        実行: _resolve_extension
        検証: 拡張子がjpgになる
        """
        result = _resolve_extension("旅行写真.jpg", "image/jpeg")
        assert result == "jpg"

    def test_resolve_extension_from_filename_jpeg(self) -> None:
        """前提条件: filenameが.jpeg、content_typeがimage/jpeg
        実行: _resolve_extension
        検証: 拡張子がjpegになる
        """
        result = _resolve_extension("寺院の写真.jpeg", "image/jpeg")
        assert result == "jpeg"

    def test_resolve_extension_raises_on_unsupported_content_type(self) -> None:
        """前提条件: content_typeがサポート外
        実行: _resolve_extension
        検証: HTTPExceptionが発生する
        """
        with pytest.raises(HTTPException) as exc_info:
            _resolve_extension(None, "image/gif")
        assert exc_info.value.status_code == 400
        assert "unsupported content_type" in exc_info.value.detail

    def test_resolve_extension_raises_on_missing_content_type(self) -> None:
        """前提条件: content_typeがNone
        実行: _resolve_extension
        検証: HTTPExceptionが発生する
        """
        with pytest.raises(HTTPException) as exc_info:
            _resolve_extension("旅行写真.jpg", None)
        assert exc_info.value.status_code == 400
        assert "content_type is required" in exc_info.value.detail

    def test_resolve_extension_raises_on_mismatched_extension(self) -> None:
        """前提条件: filenameの拡張子とcontent_typeが不一致
        実行: _resolve_extension
        検証: HTTPExceptionが発生する
        """
        with pytest.raises(HTTPException) as exc_info:
            _resolve_extension("寺院の写真.png", "image/jpeg")
        assert exc_info.value.status_code == 400
        assert "does not match content_type" in exc_info.value.detail


class TestEnsureNonEmpty:
    """_ensure_non_empty関数のテスト"""

    def test_ensure_non_empty_valid_string(self) -> None:
        """前提条件: 有効な文字列
        実行: _ensure_non_empty
        検証: トリムされた文字列が返される
        """
        result = _ensure_non_empty("  京都旅行  ", "旅行名")
        assert result == "京都旅行"

    def test_ensure_non_empty_raises_on_empty_string(self) -> None:
        """前提条件: 空文字列
        実行: _ensure_non_empty
        検証: HTTPExceptionが発生する
        """
        with pytest.raises(HTTPException) as exc_info:
            _ensure_non_empty("", "旅行名")
        assert exc_info.value.status_code == 400
        assert "旅行名 is required" in exc_info.value.detail

    def test_ensure_non_empty_raises_on_whitespace_only(self) -> None:
        """前提条件: 空白のみの文字列
        実行: _ensure_non_empty
        検証: HTTPExceptionが発生する
        """
        with pytest.raises(HTTPException) as exc_info:
            _ensure_non_empty("   ", "旅行名")
        assert exc_info.value.status_code == 400
        assert "旅行名 is required" in exc_info.value.detail
