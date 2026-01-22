"""Tests for shiny.express module placeholders and helpers."""

import ast
import os
import tempfile

from shiny.express import is_express_app
from shiny.express._is_express import DetectShinyExpressVisitor, find_magic_comment_mode


class TestIsExpressApp:
    """Tests for is_express_app function."""

    def test_is_express_app_returns_bool(self):
        """Test is_express_app returns a boolean for nonexistent file."""
        result = is_express_app("nonexistent.py", "/path/to/nowhere")
        assert isinstance(result, bool)

    def test_is_express_app_false_for_nonexistent(self):
        """Test is_express_app returns False for nonexistent file."""
        result = is_express_app("file.py", "/path/to/nonexistent")
        assert result is False

    def test_is_express_app_true_for_express_import(self):
        """Test is_express_app returns True for express import."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny.express import input\n")
            result = is_express_app("app.py", tmpdir)
            assert result is True

    def test_is_express_app_false_for_core_import(self):
        """Test is_express_app returns False for core import."""
        with tempfile.TemporaryDirectory() as tmpdir:
            app_file = os.path.join(tmpdir, "app.py")
            with open(app_file, "w") as f:
                f.write("from shiny import App, ui\n")
            result = is_express_app("app.py", tmpdir)
            assert result is False

    def test_is_express_app_false_for_non_python(self):
        """Test is_express_app returns False for non-Python file."""
        result = is_express_app("file.txt", "/path")
        assert result is False


class TestFindMagicCommentMode:
    """Tests for find_magic_comment_mode function."""

    def test_find_magic_comment_express(self):
        """Test finding express magic comment."""
        content = "# shiny_mode: express\nfrom shiny import App"
        result = find_magic_comment_mode(content)
        assert result == "express"

    def test_find_magic_comment_core(self):
        """Test finding core magic comment."""
        content = "# shiny_mode: core\nfrom shiny.express import input"
        result = find_magic_comment_mode(content)
        assert result == "core"

    def test_find_magic_comment_none(self):
        """Test no magic comment returns None."""
        content = "from shiny import App"
        result = find_magic_comment_mode(content)
        assert result is None

    def test_find_magic_comment_invalid(self):
        """Test invalid magic comment returns None."""
        content = "# shiny_mode: invalid\nfrom shiny import App"
        result = find_magic_comment_mode(content)
        assert result is None


class TestDetectShinyExpressVisitor:
    """Tests for DetectShinyExpressVisitor class."""

    def test_visitor_init(self):
        """Test visitor initialization."""
        visitor = DetectShinyExpressVisitor()
        assert visitor.found_shiny_express_import is False

    def test_visitor_detects_import_shiny_express(self):
        """Test visitor detects 'import shiny.express'."""
        code = "import shiny.express"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is True

    def test_visitor_detects_from_shiny_express_import(self):
        """Test visitor detects 'from shiny.express import ...'."""
        code = "from shiny.express import input"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is True

    def test_visitor_detects_from_shiny_import_express(self):
        """Test visitor detects 'from shiny import express'."""
        code = "from shiny import express"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is True

    def test_visitor_ignores_other_imports(self):
        """Test visitor ignores non-express imports."""
        code = "from shiny import App, ui"
        tree = ast.parse(code)
        visitor = DetectShinyExpressVisitor()
        visitor.visit(tree)
        assert visitor.found_shiny_express_import is False
