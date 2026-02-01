"""アプリケーションのロギング設定"""

import logging
import sys

from app.config.settings import get_settings


def setup_logging() -> None:
    """アプリケーション全体のロギング設定を初期化

    ルートロガーを設定し、すべてのモジュールで統一されたフォーマットで
    ログが出力されるようにする

    ログレベルはsettings.debugフラグに基づいて決定される:
    - debug=True: DEBUG レベル
    - debug=False: INFO レベル

    フォーマット: %(asctime)s - %(levelname)s - %(name)s - %(message)s
    """
    settings = get_settings()
    effective_level = settings.get_effective_log_level()
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map[effective_level]

    # ルートロガーの設定
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=settings.log_force_override,
    )
