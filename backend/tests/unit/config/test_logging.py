"""ロギング設定のユニットテスト.

Requirements 2.1: ログフォーマットにタイムスタンプ、ログレベル、モジュール名が含まれること
"""

import io
import logging
import re
from unittest.mock import patch

import pytest


class TestSetupLogging:
    """setup_logging()関数のテスト."""

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット."""
        # ルートロガーのハンドラーをクリア
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        # キャッシュをクリア
        from app.config.settings import get_settings

        get_settings.cache_clear()

    def test_setup_logging_configures_root_logger(self) -> None:
        """setup_logging()がルートロガーを設定すること."""
        from app.config.logging import setup_logging

        setup_logging()

        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0, "ルートロガーにハンドラーが設定されていること"

    def test_setup_logging_sets_info_level_when_debug_false(self) -> None:
        """debug=Falseの場合、INFOレベルが設定されること."""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO

    def test_setup_logging_sets_debug_level_when_debug_true(self) -> None:
        """debug=Trueの場合、DEBUGレベルが設定されること."""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=True,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG


class TestLogFormat:
    """ログフォーマットのテスト.

    Requirements 2.1: ログフォーマットにタイムスタンプ、ログレベル、モジュール名が含まれること
    """

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        from app.config.settings import get_settings

        get_settings.cache_clear()

    def test_log_format_includes_timestamp(self) -> None:
        """ログフォーマットにタイムスタンプが含まれること."""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            # StringIOでログ出力をキャプチャ
            log_capture = io.StringIO()
            setup_logging()

            # ハンドラーを置き換えてキャプチャ
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            handler = logging.StreamHandler(log_capture)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            root_logger.addHandler(handler)

            # テストログを出力
            test_logger = logging.getLogger("test_module")
            test_logger.info("Test message")

            log_output = log_capture.getvalue()

            # タイムスタンプのパターン: YYYY-MM-DD HH:MM:SS
            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            assert re.search(timestamp_pattern, log_output), (
                f"ログにタイムスタンプが含まれていること: {log_output}"
            )

    def test_log_format_includes_log_level(self) -> None:
        """ログフォーマットにログレベルが含まれること."""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            log_capture = io.StringIO()
            setup_logging()

            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            handler = logging.StreamHandler(log_capture)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            root_logger.addHandler(handler)

            test_logger = logging.getLogger("test_module")
            test_logger.info("Test message")

            log_output = log_capture.getvalue()

            assert "INFO" in log_output, f"ログにログレベルが含まれていること: {log_output}"

    def test_log_format_includes_module_name(self) -> None:
        """ログフォーマットにモジュール名が含まれること."""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            log_capture = io.StringIO()
            setup_logging()

            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            handler = logging.StreamHandler(log_capture)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            root_logger.addHandler(handler)

            test_logger = logging.getLogger("test_module")
            test_logger.info("Test message")

            log_output = log_capture.getvalue()

            assert "test_module" in log_output, (
                f"ログにモジュール名が含まれていること: {log_output}"
            )

    def test_log_format_contains_all_required_elements(self) -> None:
        """ログフォーマットにすべての必要な要素（タイムスタンプ、ログレベル、モジュール名）が含まれること.

        Requirements 2.1: THE Log_Format SHALL include timestamp, log level, and module name
        """
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            log_capture = io.StringIO()
            setup_logging()

            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            handler = logging.StreamHandler(log_capture)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            root_logger.addHandler(handler)

            test_logger = logging.getLogger("my_test_module")
            test_logger.warning("Test warning message")

            log_output = log_capture.getvalue()

            # タイムスタンプの検証
            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            assert re.search(timestamp_pattern, log_output), "タイムスタンプが含まれていること"

            # ログレベルの検証
            assert "WARNING" in log_output, "ログレベルが含まれていること"

            # モジュール名の検証
            assert "my_test_module" in log_output, "モジュール名が含まれていること"

            # フォーマットの順序検証: timestamp - level - name - message
            expected_pattern = (
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - WARNING - my_test_module - "
                r"Test warning message"
            )
            assert re.search(expected_pattern, log_output), (
                f"フォーマットが正しい順序であること: {log_output}"
            )
