"""プロンプトテンプレートの読み込みとレンダリング。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


@lru_cache(maxsize=128)
def load_template(template_name: str) -> str:
    """テンプレートファイルを読み込む。

    lru_cache によりテンプレート名ごとに内容をキャッシュする。
    注意: 実行中にテンプレート内容を変更しても自動反映されないため、
    必要に応じてプロセス再起動か load_template.cache_clear() でクリアする。
    """
    if not isinstance(template_name, str) or not template_name.strip():
        raise ValueError("template_name must be a non-empty string.")

    template_path = _TEMPLATES_DIR / template_name
    if not template_path.is_file():
        raise FileNotFoundError(f"template not found: {template_path}")

    return template_path.read_text(encoding="utf-8")


def render_template(template_name: str, **context: object) -> str:
    """テンプレートに値を埋め込んで文字列を返す。

    Args:
        template_name: テンプレートファイル名。
        **context: 置換に使う変数。

    Returns:
        レンダリング済み文字列。

    Raises:
        ValueError: template_name が空の場合。
        FileNotFoundError: テンプレートが存在しない場合。
        KeyError: context に不足がある場合。
    """
    template = load_template(template_name)
    try:
        return template.format(**context)
    except KeyError as exc:
        missing_key = exc.args[0]
        raise KeyError(f"Missing template variable: {missing_key} for {template_name}") from exc
