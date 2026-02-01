"""Settings設定のユニットテスト.

Requirements 4.2: debug=True の場合は DEBUG レベル
Requirements 4.3: debug=False の場合は INFO レベル以上
"""

import pytest

from app.config.settings import Settings


class TestGetEffectiveLogLevel:
    """get_effective_log_level()メソッドのテスト.

    Requirements:
    - 4.2: WHEN debug mode is enabled THEN the Logger SHALL output DEBUG level messages
    - 4.3: WHEN debug mode is disabled THEN the Logger SHALL output INFO level and above messages
    """

    def test_returns_debug_when_debug_is_true(self) -> None:
        """debug=Trueの場合、DEBUGレベルが返されること.

        **Validates: Requirements 4.2**
        """
        settings = Settings(
            debug=True,
            database_url="postgresql://test:test@localhost/test",
        )

        result = settings.get_effective_log_level()

        assert result == "DEBUG", "debug=Trueの場合、DEBUGレベルが返されること"

    def test_returns_info_when_debug_is_false(self) -> None:
        """debug=Falseの場合、INFOレベルが返されること.

        **Validates: Requirements 4.3**
        """
        settings = Settings(
            debug=False,
            database_url="postgresql://test:test@localhost/test",
        )

        result = settings.get_effective_log_level()

        assert result == "INFO", "debug=Falseの場合、INFOレベルが返されること"

    def test_returns_configured_log_level_when_debug_is_false(self) -> None:
        """debug=Falseの場合、設定されたlog_levelが返されること.

        **Validates: Requirements 4.3**
        """
        settings = Settings(
            debug=False,
            log_level="WARNING",
            database_url="postgresql://test:test@localhost/test",
        )

        result = settings.get_effective_log_level()

        assert result == "WARNING", "debug=Falseの場合、設定されたlog_levelが返されること"

    def test_debug_true_overrides_configured_log_level(self) -> None:
        """debug=Trueの場合、設定されたlog_levelに関係なくDEBUGが返されること.

        **Validates: Requirements 4.2**
        """
        settings = Settings(
            debug=True,
            log_level="ERROR",  # 明示的にERRORを設定
            database_url="postgresql://test:test@localhost/test",
        )

        result = settings.get_effective_log_level()

        assert result == "DEBUG", "debug=Trueの場合、log_level設定に関係なくDEBUGが返されること"

    def test_default_log_level_is_info(self) -> None:
        """デフォルトのlog_levelがINFOであること.

        **Validates: Requirements 4.3**
        """
        settings = Settings(
            debug=False,
            database_url="postgresql://test:test@localhost/test",
        )

        assert settings.log_level == "INFO", "デフォルトのlog_levelがINFOであること"
        assert settings.get_effective_log_level() == "INFO", (
            "debug=Falseでデフォルト設定の場合、INFOが返されること"
        )
