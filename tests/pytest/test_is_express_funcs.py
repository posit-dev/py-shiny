"""Tests for shiny.express._is_express module."""

from pathlib import Path

from shiny.express._is_express import (
    DetectShinyExpressVisitor,
    find_magic_comment_mode,
    is_express_app,
)


class TestIsExpressApp:
    """Tests for is_express_app function."""

    def test_non_python_file(self) -> None:
        """Test is_express_app returns False for non-Python files."""
        result = is_express_app("app.txt", "/some/path")
        assert result is False

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """Test is_express_app returns False for nonexistent files."""
        result = is_express_app("nonexistent.py", str(tmp_path))
        assert result is False

    def test_express_import_direct(self, tmp_path: Path) -> None:
        """Test is_express_app detects direct shiny.express import."""
        app_file = tmp_path / "app.py"
        app_file.write_text("import shiny.express\n\nprint('hello')")
        result = is_express_app("app.py", str(tmp_path))
        assert result is True

    def test_express_import_from(self, tmp_path: Path) -> None:
        """Test is_express_app detects 'from shiny.express import'."""
        app_file = tmp_path / "app.py"
        app_file.write_text("from shiny.express import input, render")
        result = is_express_app("app.py", str(tmp_path))
        assert result is True

    def test_express_import_from_shiny(self, tmp_path: Path) -> None:
        """Test is_express_app detects 'from shiny import express'."""
        app_file = tmp_path / "app.py"
        app_file.write_text("from shiny import express")
        result = is_express_app("app.py", str(tmp_path))
        assert result is True

    def test_core_app(self, tmp_path: Path) -> None:
        """Test is_express_app returns False for core app."""
        app_file = tmp_path / "app.py"
        app_file.write_text("from shiny import App, ui\nprint('hello')")
        result = is_express_app("app.py", str(tmp_path))
        assert result is False

    def test_magic_comment_express(self, tmp_path: Path) -> None:
        """Test is_express_app detects magic comment for express."""
        app_file = tmp_path / "app.py"
        app_file.write_text("# shiny_mode: express\nfrom shiny import App")
        result = is_express_app("app.py", str(tmp_path))
        assert result is True

    def test_magic_comment_core(self, tmp_path: Path) -> None:
        """Test is_express_app respects magic comment for core."""
        app_file = tmp_path / "app.py"
        app_file.write_text("# shiny_mode: core\nfrom shiny.express import input")
        result = is_express_app("app.py", str(tmp_path))
        assert result is False

    def test_absolute_path(self, tmp_path: Path) -> None:
        """Test is_express_app with absolute path and no app_dir."""
        app_file = tmp_path / "app.py"
        app_file.write_text("import shiny.express")
        result = is_express_app(str(app_file), None)
        assert result is True

    def test_syntax_error_file(self, tmp_path: Path) -> None:
        """Test is_express_app returns False for file with syntax error."""
        app_file = tmp_path / "app.py"
        app_file.write_text("def broken( syntax")
        result = is_express_app("app.py", str(tmp_path))
        assert result is False


class TestFindMagicCommentMode:
    """Tests for find_magic_comment_mode function."""

    def test_find_express_mode(self) -> None:
        """Test finding express mode magic comment."""
        content = "# shiny_mode: express\nsome code"
        result = find_magic_comment_mode(content)
        assert result == "express"

    def test_find_core_mode(self) -> None:
        """Test finding core mode magic comment."""
        content = "# shiny_mode: core\nsome code"
        result = find_magic_comment_mode(content)
        assert result == "core"

    def test_no_magic_comment(self) -> None:
        """Test when there's no magic comment."""
        content = "from shiny import App\nsome code"
        result = find_magic_comment_mode(content)
        assert result is None

    def test_magic_comment_with_spaces(self) -> None:
        """Test magic comment with extra spaces."""
        content = "#   shiny_mode:   express   \ncode"
        result = find_magic_comment_mode(content)
        assert result == "express"

    def test_invalid_magic_comment(self, capsys) -> None:
        """Test invalid magic comment value prints error."""
        content = "# shiny_mode: invalid\ncode"
        result = find_magic_comment_mode(content)
        assert result is None
        captured = capsys.readouterr()
        assert "Invalid shiny_mode" in captured.err


class TestDetectShinyExpressVisitor:
    """Tests for DetectShinyExpressVisitor class."""

    def test_initial_state(self) -> None:
        """Test visitor initial state is False."""
        visitor = DetectShinyExpressVisitor()
        assert visitor.found_shiny_express_import is False

    def test_visit_import(self) -> None:
        """Test visitor detects 'import shiny.express'."""
        import ast

        code = "import shiny.express"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is True

    def test_visit_import_from(self) -> None:
        """Test visitor detects 'from shiny.express import'."""
        import ast

        code = "from shiny.express import ui"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is True

    def test_no_express_import(self) -> None:
        """Test visitor doesn't detect non-express imports."""
        import ast

        code = "import shiny\nfrom shiny import App"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is False
