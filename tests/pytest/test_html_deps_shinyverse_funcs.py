"""Tests for shiny.ui._html_deps_shinyverse module"""

from htmltools import HTMLDependency

from shiny._versions import bslib as bslib_version
from shiny._versions import htmltools as htmltools_version
from shiny.ui._html_deps_shinyverse import components_dependencies, fill_dependency


class TestFillDependency:
    """Test fill_dependency function"""

    def test_returns_html_dependency(self):
        """Test fill_dependency returns HTMLDependency"""
        result = fill_dependency()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """Test fill_dependency has correct name"""
        result = fill_dependency()
        assert result.name == "htmltools-fill"

    def test_uses_htmltools_version(self):
        """Test fill_dependency uses htmltools version"""
        result = fill_dependency()
        assert str(result.version) == htmltools_version


class TestComponentsDependencies:
    """Test components_dependencies function"""

    def test_returns_html_dependency(self):
        """Test components_dependencies returns HTMLDependency"""
        result = components_dependencies()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """Test components_dependencies has correct name"""
        result = components_dependencies()
        assert result.name == "bslib-components"

    def test_uses_bslib_version(self):
        """Test components_dependencies uses bslib version"""
        result = components_dependencies()
        assert str(result.version) == bslib_version

    def test_include_css_default(self):
        """Test components_dependencies includes CSS by default"""
        result = components_dependencies()
        # Should have stylesheet when include_css is True (default)
        assert result is not None

    def test_include_css_false(self):
        """Test components_dependencies without CSS"""
        result = components_dependencies(include_css=False)
        assert result is not None
        # Should not include CSS stylesheet when include_css=False

    def test_include_css_true(self):
        """Test components_dependencies with explicit include_css=True"""
        result = components_dependencies(include_css=True)
        assert result is not None
