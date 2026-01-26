"""プロンプトテンプレートの読み込みとレンダリング。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


@lru_cache(maxsize=128)
def load_template(template_name: str) -> str:
    """テンプレートファイルを読み込む。"""
    if not isinstance(template_name, str) or not template_name.strip():
        raise ValueError("template_name must be a non-empty string.")

    template_path = _TEMPLATES_DIR / template_name
    if not template_path.is_file():
        raise FileNotFoundError(f"template not found: {template_path}")

    return template_path.read_text(encoding="utf-8")


def render_template(template_name: str, **context: object) -> str:
    """テンプレートに値を埋め込む。"""
    template = load_template(template_name)
    try:
        return template.format(**context)
    except KeyError as exc:
        missing_key = exc.args[0]
        raise KeyError(f"Missing template variable: {missing_key} for {template_name}") from exc
