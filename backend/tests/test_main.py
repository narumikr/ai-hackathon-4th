"""FastAPI main module tests."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def _load_app_with_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/app")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "test-project")

    sys.modules.pop("main", None)
    main = importlib.import_module("main")
    return main.app


def test_root_returns_message(monkeypatch):
    app = _load_app_with_env(monkeypatch)
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Historical Travel Agent API"}


def test_health_returns_ok(monkeypatch):
    app = _load_app_with_env(monkeypatch)
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}



class TestNoPrintStatements:
    """main.pyにprint文が存在しないことを確認するテスト.

    Requirements 1.4: THE Application SHALL NOT use print statements for logging purposes in main.py

    静的解析（AST解析）を使用してprint文の存在を検出する。
    """

    def test_main_py_has_no_print_statements(self) -> None:
        """main.pyにprint文が存在しないことを確認する.

        **Validates: Requirements 1.4**

        ASTを使用してmain.pyを解析し、print関数の呼び出しが存在しないことを検証する。
        """
        # main.pyのパスを取得
        main_py_path = Path(__file__).parent.parent / "main.py"
        assert main_py_path.exists(), f"main.py not found at {main_py_path}"

        # ファイルの内容を読み込み
        source_code = main_py_path.read_text(encoding="utf-8")

        # ASTを解析
        tree = ast.parse(source_code, filename=str(main_py_path))

        # print文を検出
        print_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # 関数呼び出しがprint関数かどうかを確認
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    print_calls.append(
                        {
                            "line": node.lineno,
                            "col": node.col_offset,
                        }
                    )

        # print文が存在しないことを確認
        assert len(print_calls) == 0, (
            f"main.pyにprint文が見つかりました。ロギングにはloggerを使用してください。\n"
            f"検出されたprint文: {print_calls}"
        )

    def test_main_py_uses_logger_instead_of_print(self) -> None:
        """main.pyがprint文の代わりにloggerを使用していることを確認する.

        **Validates: Requirements 1.4, 3.1**

        ASTを使用してmain.pyを解析し、logging.getLogger()パターンが使用されていることを検証する。
        """
        # main.pyのパスを取得
        main_py_path = Path(__file__).parent.parent / "main.py"
        assert main_py_path.exists(), f"main.py not found at {main_py_path}"

        # ファイルの内容を読み込み
        source_code = main_py_path.read_text(encoding="utf-8")

        # ASTを解析
        tree = ast.parse(source_code, filename=str(main_py_path))

        # logging.getLogger()の呼び出しを検出
        has_get_logger = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # logging.getLogger() パターンを検出
                if isinstance(node.func, ast.Attribute):
                    if (
                        node.func.attr == "getLogger"
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "logging"
                    ):
                        has_get_logger = True
                        break

        assert has_get_logger, (
            "main.pyでlogging.getLogger()が使用されていません。"
            "ロギングにはlogging.getLogger(__name__)パターンを使用してください。"
        )

    def test_main_py_has_logger_info_calls(self) -> None:
        """main.pyがlogger.info()を使用してログを出力していることを確認する.

        **Validates: Requirements 1.1, 1.2, 1.3**

        ASTを使用してmain.pyを解析し、logger.info()の呼び出しが存在することを検証する。
        """
        # main.pyのパスを取得
        main_py_path = Path(__file__).parent.parent / "main.py"
        assert main_py_path.exists(), f"main.py not found at {main_py_path}"

        # ファイルの内容を読み込み
        source_code = main_py_path.read_text(encoding="utf-8")

        # ASTを解析
        tree = ast.parse(source_code, filename=str(main_py_path))

        # logger.info()の呼び出しを検出
        logger_info_calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # logger.info() パターンを検出
                if isinstance(node.func, ast.Attribute):
                    if (
                        node.func.attr == "info"
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "logger"
                    ):
                        logger_info_calls.append(node.lineno)

        # 少なくとも3つのlogger.info()呼び出しがあることを確認
        # (起動、認証情報設定、終了)
        assert len(logger_info_calls) >= 3, (
            f"main.pyに十分なlogger.info()呼び出しがありません。"
            f"検出された呼び出し数: {len(logger_info_calls)}, 期待: 3以上"
        )
