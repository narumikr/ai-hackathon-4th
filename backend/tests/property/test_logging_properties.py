"""ロギングのプロパティベーステスト.

Property 1: Unified Log Format
**Validates: Requirements 2.1, 2.2, 2.3**

任意のログメッセージに対して、出力フォーマットが統一されていることを検証する。
- タイムスタンプ、ログレベル、モジュール名が含まれること
- フォーマットが一貫していること（timestamp - level - name - message）

Property 2: Log Level Configuration Propagation
**Validates: Requirements 3.2, 4.1**

任意のloggerインスタンスに対して、設定されたログレベルが正しく適用されることを検証する。
- debug=True の場合は DEBUG レベル
- debug=False の場合は INFO レベル
"""

from __future__ import annotations

import io
import logging
import re
from unittest.mock import patch

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Hypothesisカスタム戦略定義 ---


def _valid_module_name() -> st.SearchStrategy[str]:
    """有効なPythonモジュール名を生成するStrategy.

    Pythonのモジュール名規則に従う:
    - 英字またはアンダースコアで始まる
    - 英数字とアンダースコアのみを含む
    - 空文字列ではない

    Returns:
        有効なモジュール名のStrategy
    """
    # 最初の文字: 英字またはアンダースコア
    first_char = st.sampled_from("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
    # 残りの文字: 英数字またはアンダースコア
    rest_chars = st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_",
        min_size=0,
        max_size=30,
    )
    return st.builds(lambda f, r: f + r, first_char, rest_chars)


def _valid_log_message() -> st.SearchStrategy[str]:
    """有効なログメッセージを生成するStrategy.

    ログメッセージとして適切な文字列:
    - 空文字列ではない
    - 改行を含まない（単一行のログ）
    - printable文字のみ

    Returns:
        有効なログメッセージのStrategy
    """
    return st.text(
        alphabet=st.characters(
            min_codepoint=32,
            max_codepoint=126,
            exclude_characters="\n\r",
        ),
        min_size=1,
        max_size=100,
    ).filter(lambda s: s.strip() != "")


def _valid_log_level() -> st.SearchStrategy[int]:
    """有効なログレベルを生成するStrategy.

    Pythonのloggingモジュールで定義されている標準ログレベル:
    - DEBUG (10)
    - INFO (20)
    - WARNING (30)
    - ERROR (40)
    - CRITICAL (50)

    Returns:
        有効なログレベルのStrategy
    """
    return st.sampled_from(
        [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]
    )


@st.composite
def _log_input(draw: st.DrawFn) -> tuple[str, str, int]:
    """ログ入力データを生成するComposite Strategy.

    Args:
        draw: Hypothesisの描画関数

    Returns:
        (module_name, message, log_level)のタプル
    """
    module_name = draw(_valid_module_name())
    message = draw(_valid_log_message())
    log_level = draw(_valid_log_level())
    return module_name, message, log_level


# --- ヘルパー関数 ---


def _setup_logging_with_capture() -> tuple[logging.Logger, io.StringIO]:
    """ロギング設定を行い、出力をキャプチャするためのセットアップ.

    Returns:
        (root_logger, log_capture)のタプル
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

    root_logger = logging.getLogger()

    # 既存のハンドラーをクリア
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # キャプチャ用のハンドラーを設定
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    handler.setLevel(logging.DEBUG)  # すべてのレベルをキャプチャ
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)  # すべてのレベルを許可

    return root_logger, log_capture


def _cleanup_logging() -> None:
    """ロギング設定をクリーンアップ."""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    from app.config.settings import get_settings

    get_settings.cache_clear()


# --- Property 1: Unified Log Format ---


class TestUnifiedLogFormatProperty:
    """Property 1: Unified Log Formatのプロパティベーステスト.

    **Validates: Requirements 2.1, 2.2, 2.3**

    任意のログメッセージに対して、出力フォーマットが統一されていることを検証する。
    """

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット."""
        _cleanup_logging()

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット."""
        _cleanup_logging()

    @given(inputs=_log_input())
    @settings(max_examples=100)
    def test_property_log_output_contains_timestamp(self, inputs: tuple[str, str, int]) -> None:
        """任意のログ出力にタイムスタンプが含まれることを検証.

        **Validates: Requirements 2.1**

        前提条件:
        - 任意のモジュール名、メッセージ、ログレベルが生成される

        検証項目:
        - ログ出力にYYYY-MM-DD HH:MM:SS形式のタイムスタンプが含まれること
        """
        module_name, message, log_level = inputs

        _, log_capture = _setup_logging_with_capture()

        try:
            # テストログを出力
            test_logger = logging.getLogger(module_name)
            test_logger.log(log_level, message)

            log_output = log_capture.getvalue()

            # タイムスタンプのパターン: YYYY-MM-DD HH:MM:SS
            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            assert re.search(timestamp_pattern, log_output), (
                f"ログにタイムスタンプが含まれていること: {log_output}"
            )
        finally:
            _cleanup_logging()

    @given(inputs=_log_input())
    @settings(max_examples=100)
    def test_property_log_output_contains_log_level(self, inputs: tuple[str, str, int]) -> None:
        """任意のログ出力にログレベルが含まれることを検証.

        **Validates: Requirements 2.1**

        前提条件:
        - 任意のモジュール名、メッセージ、ログレベルが生成される

        検証項目:
        - ログ出力にログレベル名（DEBUG, INFO, WARNING, ERROR, CRITICAL）が含まれること
        """
        module_name, message, log_level = inputs

        _, log_capture = _setup_logging_with_capture()

        try:
            test_logger = logging.getLogger(module_name)
            test_logger.log(log_level, message)

            log_output = log_capture.getvalue()

            # ログレベル名を取得
            level_name = logging.getLevelName(log_level)
            assert level_name in log_output, (
                f"ログにログレベル '{level_name}' が含まれていること: {log_output}"
            )
        finally:
            _cleanup_logging()

    @given(inputs=_log_input())
    @settings(max_examples=100)
    def test_property_log_output_contains_module_name(self, inputs: tuple[str, str, int]) -> None:
        """任意のログ出力にモジュール名が含まれることを検証.

        **Validates: Requirements 2.1**

        前提条件:
        - 任意のモジュール名、メッセージ、ログレベルが生成される

        検証項目:
        - ログ出力にモジュール名が含まれること
        """
        module_name, message, log_level = inputs

        _, log_capture = _setup_logging_with_capture()

        try:
            test_logger = logging.getLogger(module_name)
            test_logger.log(log_level, message)

            log_output = log_capture.getvalue()

            assert module_name in log_output, (
                f"ログにモジュール名 '{module_name}' が含まれていること: {log_output}"
            )
        finally:
            _cleanup_logging()

    @given(inputs=_log_input())
    @settings(max_examples=100)
    def test_property_log_format_is_consistent(self, inputs: tuple[str, str, int]) -> None:
        """任意のログ出力が一貫したフォーマット（timestamp - level - name - message）であることを検証.

        **Validates: Requirements 2.2, 2.3**

        前提条件:
        - 任意のモジュール名、メッセージ、ログレベルが生成される

        検証項目:
        - ログ出力が「timestamp - level - name - message」の順序であること
        - フォーマットが統一されていること
        """
        module_name, message, log_level = inputs

        _, log_capture = _setup_logging_with_capture()

        try:
            test_logger = logging.getLogger(module_name)
            test_logger.log(log_level, message)

            log_output = log_capture.getvalue()

            # フォーマットの順序検証: timestamp - level - name - message
            level_name = logging.getLevelName(log_level)
            # メッセージ内の正規表現特殊文字をエスケープ
            escaped_message = re.escape(message)
            escaped_module_name = re.escape(module_name)

            expected_pattern = (
                rf"\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}} - "
                rf"{level_name} - {escaped_module_name} - {escaped_message}"
            )
            assert re.search(expected_pattern, log_output), (
                f"ログフォーマットが一貫していること。\n"
                f"期待パターン: {expected_pattern}\n"
                f"実際の出力: {log_output}"
            )
        finally:
            _cleanup_logging()

    @given(
        module_name1=_valid_module_name(),
        module_name2=_valid_module_name(),
        message1=_valid_log_message(),
        message2=_valid_log_message(),
        level1=_valid_log_level(),
        level2=_valid_log_level(),
    )
    @settings(max_examples=100)
    def test_property_format_consistent_across_modules(
        self,
        module_name1: str,
        module_name2: str,
        message1: str,
        message2: str,
        level1: int,
        level2: int,
    ) -> None:
        """異なるモジュールからのログ出力が同じフォーマットであることを検証.

        **Validates: Requirements 2.2**

        前提条件:
        - 2つの異なるモジュール名、メッセージ、ログレベルが生成される

        検証項目:
        - 両方のログ出力が同じフォーマット構造を持つこと
        - フォーマットがすべてのモジュールで一貫していること
        """
        _, log_capture = _setup_logging_with_capture()

        try:
            # 2つの異なるモジュールからログを出力
            logger1 = logging.getLogger(module_name1)
            logger2 = logging.getLogger(module_name2)

            logger1.log(level1, message1)
            logger2.log(level2, message2)

            log_output = log_capture.getvalue()
            log_lines = [line for line in log_output.strip().split("\n") if line]

            # 両方のログが出力されていること
            assert len(log_lines) == 2, f"2つのログが出力されていること: {log_lines}"

            # 両方のログが同じフォーマット構造を持つこと
            format_pattern = (
                r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - "
                r"(DEBUG|INFO|WARNING|ERROR|CRITICAL) - .+ - .+$"
            )

            for line in log_lines:
                assert re.match(format_pattern, line), (
                    f"ログが統一フォーマットに従っていること: {line}"
                )
        finally:
            _cleanup_logging()


# --- Property 2: Log Level Configuration Propagation ---


def _setup_logging_with_debug_mode(debug: bool) -> None:
    """指定されたdebugモードでロギング設定を初期化.

    Args:
        debug: デバッグモードの有効/無効
    """
    from app.config.settings import Settings, get_settings

    # キャッシュをクリア
    get_settings.cache_clear()

    mock_settings = Settings(
        debug=debug,
        log_force_override=True,
        database_url="postgresql://test:test@localhost/test",
    )

    with patch("app.config.logging.get_settings", return_value=mock_settings):
        from app.config.logging import setup_logging

        setup_logging()


class TestLogLevelConfigurationPropagationProperty:
    """Property 2: Log Level Configuration Propagationのプロパティベーステスト.

    **Validates: Requirements 3.2, 4.1**

    任意のloggerインスタンスに対して、設定されたログレベルが正しく適用されることを検証する。
    - debug=True の場合は DEBUG レベル
    - debug=False の場合は INFO レベル
    """

    def setup_method(self) -> None:
        """各テストの前にロガーをリセット."""
        _cleanup_logging()

    def teardown_method(self) -> None:
        """各テストの後にロガーをリセット."""
        _cleanup_logging()

    @given(module_name=_valid_module_name())
    @settings(max_examples=100)
    def test_property_debug_true_sets_debug_level(self, module_name: str) -> None:
        """debug=Trueの場合、任意のloggerインスタンスがDEBUGレベルになることを検証.

        **Validates: Requirements 3.2, 4.1**

        前提条件:
        - 任意のモジュール名が生成される
        - debug=True で設定が適用される

        検証項目:
        - loggerの有効ログレベルがDEBUGであること
        """
        try:
            _setup_logging_with_debug_mode(debug=True)

            # 任意のモジュール名でloggerを取得
            test_logger = logging.getLogger(module_name)

            # 有効なログレベルを取得（親ロガーからの継承を考慮）
            effective_level = test_logger.getEffectiveLevel()

            assert effective_level == logging.DEBUG, (
                f"debug=True の場合、logger '{module_name}' の有効レベルは DEBUG であること。"
                f"実際のレベル: {logging.getLevelName(effective_level)}"
            )
        finally:
            _cleanup_logging()

    @given(module_name=_valid_module_name())
    @settings(max_examples=100)
    def test_property_debug_false_sets_info_level(self, module_name: str) -> None:
        """debug=Falseの場合、任意のloggerインスタンスがINFOレベルになることを検証.

        **Validates: Requirements 3.2, 4.1**

        前提条件:
        - 任意のモジュール名が生成される
        - debug=False で設定が適用される

        検証項目:
        - loggerの有効ログレベルがINFOであること
        """
        try:
            _setup_logging_with_debug_mode(debug=False)

            # 任意のモジュール名でloggerを取得
            test_logger = logging.getLogger(module_name)

            # 有効なログレベルを取得（親ロガーからの継承を考慮）
            effective_level = test_logger.getEffectiveLevel()

            assert effective_level == logging.INFO, (
                f"debug=False の場合、logger '{module_name}' の有効レベルは INFO であること。"
                f"実際のレベル: {logging.getLevelName(effective_level)}"
            )
        finally:
            _cleanup_logging()

    @given(
        module_names=st.lists(_valid_module_name(), min_size=2, max_size=10, unique=True),
        debug_mode=st.booleans(),
    )
    @settings(max_examples=100)
    def test_property_all_loggers_have_consistent_level(
        self, module_names: list[str], debug_mode: bool
    ) -> None:
        """複数のloggerインスタンスが同じ有効ログレベルを持つことを検証.

        **Validates: Requirements 3.2**

        前提条件:
        - 複数の異なるモジュール名が生成される
        - debug_mode が True または False

        検証項目:
        - すべてのloggerが同じ有効ログレベルを持つこと
        - debug=True なら DEBUG、debug=False なら INFO
        """
        try:
            _setup_logging_with_debug_mode(debug=debug_mode)

            expected_level = logging.DEBUG if debug_mode else logging.INFO

            # 複数のloggerを取得し、すべてが同じレベルであることを確認
            for module_name in module_names:
                test_logger = logging.getLogger(module_name)
                effective_level = test_logger.getEffectiveLevel()

                assert effective_level == expected_level, (
                    f"debug={debug_mode} の場合、すべてのloggerが "
                    f"{logging.getLevelName(expected_level)} レベルであること。"
                    f"logger '{module_name}' の実際のレベル: "
                    f"{logging.getLevelName(effective_level)}"
                )
        finally:
            _cleanup_logging()

    @given(module_name=_valid_module_name())
    @settings(max_examples=100)
    def test_property_debug_messages_output_when_debug_true(self, module_name: str) -> None:
        """debug=Trueの場合、DEBUGレベルのメッセージが出力されることを検証.

        **Validates: Requirements 3.2, 4.1**

        前提条件:
        - 任意のモジュール名が生成される
        - debug=True で設定が適用される

        検証項目:
        - DEBUGレベルのログメッセージが実際に出力されること
        """
        try:
            _setup_logging_with_debug_mode(debug=True)

            # キャプチャ用のハンドラーを設定
            root_logger = logging.getLogger()
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            handler.setLevel(logging.DEBUG)
            root_logger.addHandler(handler)

            # DEBUGレベルのログを出力
            test_logger = logging.getLogger(module_name)
            debug_message = "test_debug_message"
            test_logger.debug(debug_message)

            log_output = log_capture.getvalue()

            assert debug_message in log_output, (
                f"debug=True の場合、DEBUGメッセージが出力されること。"
                f"出力: {log_output}"
            )
            assert "DEBUG" in log_output, (
                f"出力にDEBUGレベルが含まれること。出力: {log_output}"
            )
        finally:
            _cleanup_logging()

    @given(module_name=_valid_module_name())
    @settings(max_examples=100)
    def test_property_debug_messages_suppressed_when_debug_false(self, module_name: str) -> None:
        """debug=Falseの場合、DEBUGレベルのメッセージが抑制されることを検証.

        **Validates: Requirements 3.2, 4.1**

        前提条件:
        - 任意のモジュール名が生成される
        - debug=False で設定が適用される

        検証項目:
        - DEBUGレベルのログメッセージが出力されないこと
        - INFOレベルのログメッセージは出力されること
        """
        try:
            _setup_logging_with_debug_mode(debug=False)

            # キャプチャ用のハンドラーを設定
            root_logger = logging.getLogger()
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            handler.setLevel(logging.DEBUG)  # ハンドラーはすべてのレベルを受け入れる
            root_logger.addHandler(handler)

            # DEBUGとINFOレベルのログを出力
            test_logger = logging.getLogger(module_name)
            debug_message = "test_debug_message_should_not_appear"
            info_message = "test_info_message_should_appear"
            test_logger.debug(debug_message)
            test_logger.info(info_message)

            log_output = log_capture.getvalue()

            assert debug_message not in log_output, (
                f"debug=False の場合、DEBUGメッセージが抑制されること。"
                f"出力: {log_output}"
            )
            assert info_message in log_output, (
                f"debug=False の場合でも、INFOメッセージは出力されること。"
                f"出力: {log_output}"
            )
        finally:
            _cleanup_logging()
