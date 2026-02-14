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

    # 一時的にAI関連ログだけを見たい場合のフォーカスモード
    if settings.log_ai_focus:
        logging.getLogger("app.infrastructure.ai.gemini_client").setLevel(logging.INFO)
        logging.getLogger("app.application.use_cases.generate_travel_guide").setLevel(logging.INFO)
        logging.getLogger("app.interfaces.api.v1.travel_guides").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("cachecontrol").setLevel(logging.WARNING)
        logging.getLogger("google_genai").setLevel(logging.WARNING)
        return

    # SQL文ログのノイズを抑制するため、通常運用ではsqlalchemy.engineをWARNINGに固定
    if not settings.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
