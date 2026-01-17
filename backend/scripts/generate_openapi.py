"""OpenAPI仕様書生成スクリプト."""

import json
import sys
from argparse import ArgumentParser
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app


def generate_openapi_schema(output_path: Path) -> None:
    """OpenAPIスキーマを生成する.

    Args:
        output_path: 出力ファイルパス
    """
    try:
        # OpenAPIスキーマを取得
        schema = app.openapi()

        # 出力ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # JSON形式で出力
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)

        print(f"OpenAPIスキーマを生成しました: {output_path}")

    except Exception as e:
        print(f"OpenAPIスキーマの生成中にエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """メイン処理."""
    parser = ArgumentParser(description="Generate OpenAPI schema")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent.parent / "docs/backend/openapi.json",
        help="Output file path (default: docs/backend/openapi.json)",
    )
    args = parser.parse_args()

    generate_openapi_schema(args.output)


if __name__ == "__main__":
    main()
