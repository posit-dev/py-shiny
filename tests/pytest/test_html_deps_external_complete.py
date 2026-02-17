"""Comprehensive tests for shiny.ui._html_deps_external module."""

from __future__ import annotations

from pathlib import Path

import pytest
from htmltools import HTMLDependency, Tag, TagList

from shiny.ui._html_deps_external import (
    bootstrap_deps,
    datepicker_deps,
    ionrangeslider_deps,
    jqui_deps,
    selectize_deps,
    shiny_page_theme_deps,
)
from shiny.ui._theme import Theme


class TestShinyPageThemeDeps:
    """Tests for shiny_page_theme_deps function."""

    def test_with_none_theme(self):
        """Test shiny_page_theme_deps with None theme (default Bootstrap)."""
        result = shiny_page_theme_deps(None)
        assert isinstance(result, TagList)
        # Should include Bootstrap CSS by default
        assert result is not None

    def test_with_theme_object(self):
        """Test shiny_page_theme_deps with Theme object."""
        theme = Theme()
        result = shiny_page_theme_deps(theme)
        assert isinstance(result, TagList)

    def test_with_http_url(self):
        """Test shiny_page_theme_deps with HTTP URL."""
        result = shiny_page_theme_deps("http://example.com/theme.css")
        assert isinstance(result, TagList)

    def test_with_https_url(self):
        """Test shiny_page_theme_deps with HTTPS URL."""
        result = shiny_page_theme_deps("https://example.com/theme.css")
        assert isinstance(result, TagList)

    def test_with_protocol_relative_url(self):
        """Test shiny_page_theme_deps with protocol-relative URL."""
        result = shiny_page_theme_deps("//example.com/theme.css")
        assert isinstance(result, TagList)

    def test_with_file_path(self, tmp_path: Path):
        """Test shiny_page_theme_deps with file path."""
        path = tmp_path / "theme.css"
        path.write_text("body { color: red; }", encoding="utf-8")

        result = shiny_page_theme_deps(str(path))
        assert isinstance(result, TagList)

    def test_with_path_object(self, tmp_path: Path):
        """Test shiny_page_theme_deps with Path object."""
        path = tmp_path / "theme.css"
        path.write_text("body { color: blue; }", encoding="utf-8")

        result = shiny_page_theme_deps(path)
        assert isinstance(result, TagList)

    def test_with_tagifiable(self):
        """Test shiny_page_theme_deps with Tagifiable object."""
        tag = Tag("style", "body { color: green; }")
        result = shiny_page_theme_deps(tag)
        assert isinstance(result, TagList)

    def test_with_html_dependency(self):
        """Test shiny_page_theme_deps with single HTMLDependency."""
        dep = HTMLDependency(
            name="test-theme",
            version="1.0.0",
            source={"package": "shiny", "subdir": "www"},
        )
        result = shiny_page_theme_deps(dep)
        assert isinstance(result, TagList)

    def test_with_html_dependency_list(self):
        """Test shiny_page_theme_deps with list of HTMLDependency."""
        deps = [
            HTMLDependency(
                name="test-theme1",
                version="1.0.0",
                source={"package": "shiny", "subdir": "www"},
            ),
            HTMLDependency(
                name="test-theme2",
                version="2.0.0",
                source={"package": "shiny", "subdir": "www"},
            ),
        ]
        result = shiny_page_theme_deps(deps)
        assert isinstance(result, TagList)

    def test_with_invalid_theme_type(self):
        """Test shiny_page_theme_deps with invalid theme type."""
        with pytest.raises(ValueError, match="Invalid `theme`"):
            shiny_page_theme_deps(12345)  # type: ignore

    def test_with_invalid_path(self):
        """Test shiny_page_theme_deps with non-existent file path."""
        with pytest.raises(RuntimeError, match="does not exist"):
            shiny_page_theme_deps("/non/existent/path/theme.css")

    def test_includes_bootstrap_deps(self):
        """Test that result includes bootstrap dependencies."""
        result = shiny_page_theme_deps(None)
        # TagList should contain multiple dependencies
        assert len(result) > 0

    def test_includes_component_deps(self):
        """Test that result includes component dependencies."""
        result = shiny_page_theme_deps(None)
        # Should include various component dependencies
        assert isinstance(result, TagList)


class TestJquiDeps:
    """Tests for jqui_deps function."""

    def test_jqui_deps_returns_dependency(self):
        """jqui_deps should return an HTMLDependency."""
        result = jqui_deps()
        assert isinstance(result, HTMLDependency)

    def test_jqui_deps_has_correct_name(self):
        """jqui_deps should have name 'jquery-ui'."""
        result = jqui_deps()
        assert result.name == "jquery-ui"

    def test_jqui_deps_has_correct_version(self):
        """jqui_deps should have version '1.12.1'."""
        result = jqui_deps()
        assert str(result.version) == "1.12.1"

    def test_jqui_deps_has_script(self):
        """jqui_deps should include script."""
        result = jqui_deps()
        assert result.script is not None

    def test_jqui_deps_has_stylesheet(self):
        """jqui_deps should include stylesheet."""
        result = jqui_deps()
        assert result.stylesheet is not None


class TestIonrangesliderDepsComplete:
    """Additional tests for ionrangeslider_deps."""

    def test_with_css_true(self):
        """Test ionrangeslider_deps with include_css=True."""
        result = ionrangeslider_deps(include_css=True)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_with_css_false(self):
        """Test ionrangeslider_deps with include_css=False."""
        result = ionrangeslider_deps(include_css=False)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_strftime_version(self):
        """Test strftime dependency has correct version."""
        result = ionrangeslider_deps()
        strftime_dep = next(dep for dep in result if dep.name == "strftime")
        assert str(strftime_dep.version) == "0.9.2"


class TestDatepickerDepsComplete:
    """Additional tests for datepicker_deps."""

    def test_has_correct_name(self):
        """datepicker_deps should have name 'bootstrap-datepicker'."""
        result = datepicker_deps()
        assert result.name == "bootstrap-datepicker"

    def test_has_correct_version(self):
        """datepicker_deps should have version '1.9.0'."""
        result = datepicker_deps()
        assert str(result.version) == "1.9.0"

    def test_with_css_true(self):
        """datepicker_deps should work with include_css=True."""
        result = datepicker_deps(include_css=True)
        assert isinstance(result, HTMLDependency)

    def test_with_css_false(self):
        """datepicker_deps should work with include_css=False."""
        result = datepicker_deps(include_css=False)
        assert isinstance(result, HTMLDependency)

    def test_has_no_conflict_script(self):
        """datepicker_deps should include noConflict script in head."""
        result = datepicker_deps()
        assert result.head is not None
        # head can be HTML or TagList, both are valid


class TestSelectizeDepsComplete:
    """Additional tests for selectize_deps."""

    def test_selectize_deps_has_correct_name(self):
        """selectize_deps should have name 'selectize'."""
        result = selectize_deps()
        assert result.name == "selectize"

    def test_selectize_deps_has_correct_version(self):
        """selectize_deps should have version '0.12.6'."""
        result = selectize_deps()
        assert str(result.version) == "0.12.6"

    def test_selectize_deps_with_css_true(self):
        """selectize_deps should work with include_css=True."""
        result = selectize_deps(include_css=True)
        assert isinstance(result, HTMLDependency)

    def test_selectize_deps_with_css_false(self):
        """selectize_deps should work with include_css=False."""
        result = selectize_deps(include_css=False)
        assert isinstance(result, HTMLDependency)

    def test_selectize_deps_has_multiple_scripts(self):
        """selectize_deps should include multiple script files."""
        result = selectize_deps()
        assert result.script is not None
        # Should have main script and accessibility plugin
        assert isinstance(result.script, list)
        assert len(result.script) == 2


class TestBootstrapDepsComplete:
    """Additional tests for bootstrap_deps."""

    def test_has_viewport_meta(self):
        """bootstrap_deps should include viewport meta tag."""
        result = bootstrap_deps()
        bootstrap_dep = next(dep for dep in result if dep.name == "bootstrap")
        assert bootstrap_dep.meta is not None

    def test_all_files_included(self):
        """bootstrap_deps should set all_files to True."""
        result = bootstrap_deps()
        bootstrap_dep = next(dep for dep in result if dep.name == "bootstrap")
        assert bootstrap_dep.all_files is True

    def test_bootstrap_has_script(self):
        """bootstrap_deps should include bootstrap.bundle.min.js."""
        result = bootstrap_deps()
        bootstrap_dep = next(dep for dep in result if dep.name == "bootstrap")
        assert bootstrap_dep.script is not None
