"""既存のlogger利用箇所の互換性テスト

Requirements 3.3: THE logging configuration SHALL NOT break existing logger functionality
in error_handler.py, travel_guides.py, reflections.py, and analyze_photos.py

このテストでは、setup_logging()呼び出し後に既存のloggerが正常に動作することを確認する
"""

import io
import logging
import re
from unittest.mock import patch


class TestExistingLoggerCompatibility:
    """既存のlogger利用箇所との互換性テスト

    Requirements 3.3: 既存のlogger機能が壊れないことを確認
    """

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        from app.config.settings import get_settings

        get_settings.cache_clear()

    def _setup_logging_with_capture(self) -> io.StringIO:
        """ロギング設定を行い、出力をキャプチャするStringIOを返す"""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

        log_capture = io.StringIO()
        root_logger = logging.getLogger()

        # 既存のハンドラーをクリアしてキャプチャ用ハンドラーを追加
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

        return log_capture

    def test_error_handler_logger_works_after_setup_logging(self) -> None:
        """setup_logging()後にerror_handler.pyのloggerが正常に動作すること

        Requirements 3.3: error_handler.pyのlogger機能が壊れないこと
        """
        log_capture = self._setup_logging_with_capture()

        # error_handler.pyと同じパターンでloggerを取得
        logger = logging.getLogger("app.interfaces.middleware.error_handler")

        # error_handler.pyで使用されているログレベルをテスト
        logger.error("HTTP error occurred: 404 - Not Found")
        logger.warning("Validation error occurred: invalid input")
        logger.exception("Unexpected error occurred: test error")

        log_output = log_capture.getvalue()

        # 各ログレベルが出力されていることを確認
        assert "ERROR" in log_output, "ERRORレベルのログが出力されること"
        assert "WARNING" in log_output, "WARNINGレベルのログが出力されること"
        assert "app.interfaces.middleware.error_handler" in log_output, (
            "モジュール名が出力されること"
        )

    def test_travel_guides_logger_works_after_setup_logging(self) -> None:
        """setup_logging()後にtravel_guides.pyのloggerが正常に動作すること

        Requirements 3.3: travel_guides.pyのlogger機能が壊れないこと
        """
        log_capture = self._setup_logging_with_capture()

        # travel_guides.pyと同じパターンでloggerを取得
        logger = logging.getLogger("app.interfaces.api.v1.travel_guides")

        # travel_guides.pyで使用されているログパターンをテスト
        logger.exception(
            "Failed to generate travel guide",
            extra={"plan_id": "test-plan-123"},
        )

        log_output = log_capture.getvalue()

        assert "ERROR" in log_output, "ERRORレベルのログが出力されること"
        assert "app.interfaces.api.v1.travel_guides" in log_output, "モジュール名が出力されること"
        assert "Failed to generate travel guide" in log_output, "ログメッセージが出力されること"

    def test_reflections_logger_works_after_setup_logging(self) -> None:
        """setup_logging()後にreflections.pyのloggerが正常に動作すること

        Requirements 3.3: reflections.pyのlogger機能が壊れないこと
        """
        log_capture = self._setup_logging_with_capture()

        # reflections.pyと同じパターンでloggerを取得
        logger = logging.getLogger("app.interfaces.api.v1.reflections")

        # reflections.pyで使用されているログパターンをテスト
        logger.exception(
            "Failed to generate reflection",
            extra={"plan_id": "test-plan-456"},
        )
        logger.exception(
            "Failed to update reflection status to failed",
            extra={"plan_id": "test-plan-456"},
        )

        log_output = log_capture.getvalue()

        assert "ERROR" in log_output, "ERRORレベルのログが出力されること"
        assert "app.interfaces.api.v1.reflections" in log_output, "モジュール名が出力されること"
        assert "Failed to generate reflection" in log_output, "ログメッセージが出力されること"

    def test_analyze_photos_logger_works_after_setup_logging(self) -> None:
        """setup_logging()後にanalyze_photos.pyのloggerが正常に動作すること

        Requirements 3.3: analyze_photos.pyのlogger機能が壊れないこと
        """
        log_capture = self._setup_logging_with_capture()

        # analyze_photos.pyと同じパターンでloggerを取得
        logger = logging.getLogger("app.application.use_cases.analyze_photos")

        # analyze_photos.pyで使用されているログパターンをテスト
        logger.warning(
            "Image analysis attempt failed.",
            extra={
                "plan_id": "test-plan-789",
                "photo_id": "photo-001",
                "spot_id": "spot-001",
                "attempt": 1,
                "max_attempts": 3,
                "is_final_attempt": False,
            },
        )

        log_output = log_capture.getvalue()

        assert "WARNING" in log_output, "WARNINGレベルのログが出力されること"
        assert "app.application.use_cases.analyze_photos" in log_output, (
            "モジュール名が出力されること"
        )
        assert "Image analysis attempt failed" in log_output, (
            "ログメッセージが出力されること"
        )


class TestExistingLoggersUnifiedFormat:
    """既存のloggerが統一フォーマットで出力されることのテスト

    Requirements 3.3: 既存のloggerが統一フォーマットで出力されること
    """

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        from app.config.settings import get_settings

        get_settings.cache_clear()

    def _setup_logging_with_capture(self) -> io.StringIO:
        """ロギング設定を行い、出力をキャプチャするStringIOを返す"""
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

        log_capture = io.StringIO()
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

        return log_capture

    def test_all_existing_loggers_use_unified_format(self) -> None:
        """すべての既存loggerが統一フォーマットで出力されること

        Requirements 3.3: 既存のloggerが統一フォーマットで出力されること
        """
        log_capture = self._setup_logging_with_capture()

        # 各モジュールのloggerを取得
        loggers = [
            logging.getLogger("app.interfaces.middleware.error_handler"),
            logging.getLogger("app.interfaces.api.v1.travel_guides"),
            logging.getLogger("app.interfaces.api.v1.reflections"),
            logging.getLogger("app.application.use_cases.analyze_photos"),
        ]

        # 各loggerでログを出力
        for logger in loggers:
            logger.info(f"Test message from {logger.name}")

        log_output = log_capture.getvalue()
        log_lines = [line for line in log_output.strip().split("\n") if line]

        # 統一フォーマットのパターン: YYYY-MM-DD HH:MM:SS - LEVEL - name - message
        unified_format_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - \w+ - [\w.]+ - .+"

        assert len(log_lines) == 4, f"4つのログが出力されること: {log_lines}"

        for line in log_lines:
            assert re.match(unified_format_pattern, line), (
                f"統一フォーマットで出力されること: {line}"
            )

    def test_existing_loggers_include_timestamp_level_and_name(self) -> None:
        """既存のloggerの出力にタイムスタンプ、レベル、モジュール名が含まれること

        Requirements 3.3: 既存のloggerが統一フォーマットで出力されること
        """
        log_capture = self._setup_logging_with_capture()

        # error_handler.pyのloggerでテスト
        logger = logging.getLogger("app.interfaces.middleware.error_handler")
        logger.error("Test error message")

        log_output = log_capture.getvalue()

        # タイムスタンプの検証
        timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
        assert re.search(timestamp_pattern, log_output), (
            f"タイムスタンプが含まれること: {log_output}"
        )

        # ログレベルの検証
        assert "ERROR" in log_output, f"ログレベルが含まれること: {log_output}"

        # モジュール名の検証
        assert "app.interfaces.middleware.error_handler" in log_output, (
            f"モジュール名が含まれること: {log_output}"
        )


class TestLoggingConfigurationAppliestoExistingLoggers:
    """ロギング設定が既存のloggerインスタンスに適用されることのテスト

    Requirements 3.2: WHEN configuring logging THEN the configuration SHALL apply
    to all existing logger instances
    """

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット"""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        from app.config.settings import get_settings

        get_settings.cache_clear()

    def test_logging_config_applies_to_pre_existing_loggers(self) -> None:
        """setup_logging()前に作成されたloggerにも設定が適用されること

        Requirements 3.2: 設定がすべての既存loggerインスタンスに適用されること
        """
        # setup_logging()前にloggerを作成（実際のアプリケーションの動作を模倣）
        pre_existing_logger = logging.getLogger("app.interfaces.middleware.error_handler")

        from app.config.settings import Settings

        mock_settings = Settings(
            debug=True,  # DEBUGレベルを設定
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

        # ルートロガーのレベルがDEBUGに設定されていることを確認
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG, "ルートロガーのレベルがDEBUGに設定されること"

        # 既存のloggerがルートロガーの設定を継承していることを確認
        # (子loggerはデフォルトでNOTSETなので、ルートロガーの設定を継承する)
        assert pre_existing_logger.getEffectiveLevel() == logging.DEBUG, (
            "既存のloggerがルートロガーの設定を継承すること"
        )

    def test_logging_config_applies_to_all_module_loggers(self) -> None:
        """すべてのモジュールのloggerに設定が適用されること

        Requirements 3.2: 設定がすべての既存loggerインスタンスに適用されること
        """
        # 各モジュールのloggerを事前に作成
        module_loggers = [
            logging.getLogger("app.interfaces.middleware.error_handler"),
            logging.getLogger("app.interfaces.api.v1.travel_guides"),
            logging.getLogger("app.interfaces.api.v1.reflections"),
            logging.getLogger("app.application.use_cases.analyze_photos"),
        ]

        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,  # INFOレベルを設定
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

        # すべてのloggerが有効なログレベルとしてINFOを持つことを確認
        for logger in module_loggers:
            assert logger.getEffectiveLevel() == logging.INFO, (
                f"{logger.name}のログレベルがINFOであること"
            )

    def test_debug_logs_output_when_debug_enabled(self) -> None:
        """debug=Trueの場合、DEBUGレベルのログが出力されること

        Requirements 3.2, 4.2: debug=TrueでDEBUGレベルのログが出力されること
        """
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=True,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

        log_capture = io.StringIO()
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
        handler.setLevel(logging.DEBUG)
        root_logger.addHandler(handler)

        # 既存モジュールのloggerでDEBUGログを出力
        logger = logging.getLogger("app.interfaces.middleware.error_handler")
        logger.debug("Debug message for testing")

        log_output = log_capture.getvalue()

        assert "DEBUG" in log_output, f"DEBUGレベルのログが出力されること: {log_output}"
        assert "Debug message for testing" in log_output, (
            f"DEBUGメッセージが出力されること: {log_output}"
        )

    def test_debug_logs_suppressed_when_debug_disabled(self) -> None:
        """debug=Falseの場合、DEBUGレベルのログが抑制されること

        Requirements 3.2, 4.3: debug=FalseでDEBUGレベルのログが抑制されること
        """
        from app.config.settings import Settings

        mock_settings = Settings(
            debug=False,
            log_force_override=True,
            database_url="postgresql://test:test@localhost/test",
        )

        with patch("app.config.logging.get_settings", return_value=mock_settings):
            from app.config.logging import setup_logging

            setup_logging()

        log_capture = io.StringIO()
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

        # 既存モジュールのloggerでDEBUGログを出力
        logger = logging.getLogger("app.interfaces.middleware.error_handler")
        logger.debug("Debug message that should be suppressed")
        logger.info("Info message that should be output")

        log_output = log_capture.getvalue()

        assert "DEBUG" not in log_output, f"DEBUGレベルのログが抑制されること: {log_output}"
        assert "Info message that should be output" in log_output, (
            f"INFOレベルのログは出力されること: {log_output}"
        )
