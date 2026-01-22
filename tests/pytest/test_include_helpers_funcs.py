"""Tests for shiny.ui._include_helpers module."""

from pathlib import Path

import pytest
from htmltools import Tag

from shiny.ui._include_helpers import include_css, include_js


class TestIncludeJs:
    """Tests for include_js function."""

    def test_include_js_inline(self, tmp_path: Path) -> None:
        """Test include_js with inline method."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');")
        result = include_js(js_file, method="inline")
        assert isinstance(result, Tag)
        assert result.name == "script"
        html = str(result)
        assert "console.log" in html

    def test_include_js_link(self, tmp_path: Path) -> None:
        """Test include_js with link method."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');")
        result = include_js(js_file, method="link")
        assert isinstance(result, Tag)
        assert result.name == "script"

    def test_include_js_link_files(self, tmp_path: Path) -> None:
        """Test include_js with link_files method."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');")
        result = include_js(js_file, method="link_files")
        assert isinstance(result, Tag)
        assert result.name == "script"

    def test_include_js_with_kwargs(self, tmp_path: Path) -> None:
        """Test include_js with additional attributes."""
        js_file = tmp_path / "test.js"
        js_file.write_text("console.log('hello');")
        result = include_js(js_file, method="inline", id="my-script")
        html = str(result)
        assert 'id="my-script"' in html

    def test_include_js_invalid_path(self) -> None:
        """Test include_js with invalid path raises error."""
        with pytest.raises(RuntimeError, match="does not exist"):
            include_js("/nonexistent/path.js")


class TestIncludeCss:
    """Tests for include_css function."""

    def test_include_css_inline(self, tmp_path: Path) -> None:
        """Test include_css with inline method."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: red; }")
        result = include_css(css_file, method="inline")
        assert isinstance(result, Tag)
        assert result.name == "style"
        html = str(result)
        assert "color: red" in html

    def test_include_css_link(self, tmp_path: Path) -> None:
        """Test include_css with link method."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: red; }")
        result = include_css(css_file, method="link")
        assert isinstance(result, Tag)
        assert result.name == "link"
        html = str(result)
        assert 'rel="stylesheet"' in html

    def test_include_css_link_files(self, tmp_path: Path) -> None:
        """Test include_css with link_files method."""
        css_file = tmp_path / "test.css"
        css_file.write_text("body { color: red; }")
        result = include_css(css_file, method="link_files")
        assert isinstance(result, Tag)
        assert result.name == "link"

    def test_include_css_invalid_path(self) -> None:
        """Test include_css with invalid path raises error."""
        with pytest.raises(RuntimeError, match="does not exist"):
            include_css("/nonexistent/path.css")


class TestIncludeIntegration:
    """Integration tests for include helpers."""

    def test_include_js_with_multiple_files(self, tmp_path: Path) -> None:
        """Test include_js can include related files."""
        js_dir = tmp_path / "js"
        js_dir.mkdir()
        main_js = js_dir / "main.js"
        main_js.write_text("import './helper.js'; console.log('main');")
        helper_js = js_dir / "helper.js"
        helper_js.write_text("console.log('helper');")

        result = include_js(main_js, method="link_files")
        assert isinstance(result, Tag)

    def test_include_css_with_path_object(self, tmp_path: Path) -> None:
        """Test include_css with Path object."""
        css_file = tmp_path / "style.css"
        css_file.write_text(".test { color: blue; }")
        result = include_css(Path(css_file), method="inline")
        html = str(result)
        assert "color: blue" in html
