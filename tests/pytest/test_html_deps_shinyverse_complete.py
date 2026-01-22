"""Comprehensive tests for shiny.ui._html_deps_shinyverse module."""

from __future__ import annotations

from htmltools import HTMLDependency

from shiny._versions import bslib as bslib_version
from shiny._versions import htmltools as htmltools_version
from shiny.ui._html_deps_shinyverse import components_dependencies, fill_dependency


class TestFillDependencyComplete:
    """Comprehensive tests for fill_dependency function."""

    def test_returns_html_dependency(self):
        """fill_dependency should return an HTMLDependency object."""
        result = fill_dependency()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """fill_dependency should have name 'htmltools-fill'."""
        result = fill_dependency()
        assert result.name == "htmltools-fill"

    def test_has_correct_version(self):
        """fill_dependency should use htmltools version."""
        result = fill_dependency()
        assert str(result.version) == htmltools_version

    def test_has_source_package(self):
        """fill_dependency should have source package 'shiny'."""
        result = fill_dependency()
        assert result.source is not None
        assert result.source.get("package") == "shiny"

    def test_has_source_subdir(self):
        """fill_dependency should have correct source subdir."""
        result = fill_dependency()
        assert result.source is not None
        assert "htmltools" in result.source.get("subdir", "")
        assert "fill" in result.source.get("subdir", "")

    def test_has_stylesheet(self):
        """fill_dependency should include fill.css stylesheet."""
        result = fill_dependency()
        assert result.stylesheet is not None

    def test_is_reusable(self):
        """fill_dependency should be callable multiple times."""
        result1 = fill_dependency()
        result2 = fill_dependency()
        assert result1.name == result2.name
        assert result1.version == result2.version


class TestComponentsDependenciesComplete:
    """Comprehensive tests for components_dependencies function."""

    def test_returns_html_dependency(self):
        """components_dependencies should return an HTMLDependency object."""
        result = components_dependencies()
        assert isinstance(result, HTMLDependency)

    def test_has_correct_name(self):
        """components_dependencies should have name 'bslib-components'."""
        result = components_dependencies()
        assert result.name == "bslib-components"

    def test_has_correct_version(self):
        """components_dependencies should use bslib version."""
        result = components_dependencies()
        assert str(result.version) == bslib_version

    def test_has_source_package(self):
        """components_dependencies should have source package 'shiny'."""
        result = components_dependencies()
        assert result.source is not None
        assert result.source.get("package") == "shiny"

    def test_has_source_subdir(self):
        """components_dependencies should have correct source subdir."""
        result = components_dependencies()
        assert result.source is not None
        assert "bslib" in result.source.get("subdir", "")
        assert "components" in result.source.get("subdir", "")

    def test_has_scripts(self):
        """components_dependencies should include JavaScript files."""
        result = components_dependencies()
        assert result.script is not None
        assert isinstance(result.script, list)
        # Should have at least 2 scripts
        assert len(result.script) >= 2

    def test_has_components_script(self):
        """components_dependencies should include components.min.js."""
        result = components_dependencies()
        assert result.script is not None
        script_sources = [
            s.get("src", "") if isinstance(s, dict) else s for s in result.script
        ]
        assert any("components.min.js" in src for src in script_sources)

    def test_has_web_components_script(self):
        """components_dependencies should include web-components.min.js."""
        result = components_dependencies()
        assert result.script is not None
        script_sources = [
            s.get("src", "") if isinstance(s, dict) else s for s in result.script
        ]
        assert any("web-components.min.js" in src for src in script_sources)

    def test_web_components_is_module(self):
        """web-components.min.js should be loaded as ES module."""
        result = components_dependencies()
        assert result.script is not None
        # Find web-components script and check if it has type="module"
        web_comp_script = next(
            (
                s
                for s in result.script
                if isinstance(s, dict) and "web-components.min.js" in s.get("src", "")
            ),
            None,
        )
        assert web_comp_script is not None
        assert web_comp_script.get("type") == "module"

    def test_include_css_default_true(self):
        """components_dependencies should include CSS by default."""
        result = components_dependencies()
        # Default behavior includes CSS
        assert result is not None

    def test_include_css_explicit_true(self):
        """components_dependencies should include CSS when explicitly True."""
        result = components_dependencies(include_css=True)
        assert result is not None
        # Should have stylesheet when include_css=True

    def test_include_css_false(self):
        """components_dependencies should work without CSS."""
        result = components_dependencies(include_css=False)
        assert result is not None
        assert isinstance(result, HTMLDependency)

    def test_is_reusable(self):
        """components_dependencies should be callable multiple times."""
        result1 = components_dependencies()
        result2 = components_dependencies()
        assert result1.name == result2.name
        assert result1.version == result2.version

    def test_different_css_settings(self):
        """components_dependencies with different CSS settings should work."""
        result_with_css = components_dependencies(include_css=True)
        result_without_css = components_dependencies(include_css=False)
        # Both should return valid dependencies
        assert isinstance(result_with_css, HTMLDependency)
        assert isinstance(result_without_css, HTMLDependency)
        # Same name and version
        assert result_with_css.name == result_without_css.name
        assert result_with_css.version == result_without_css.version


class TestModuleConstants:
    """Tests for module-level constants and paths."""

    def test_module_imports_correctly(self):
        """Module should import correctly."""
        from shiny.ui import _html_deps_shinyverse

        assert _html_deps_shinyverse is not None
        # Module exists and is importable

    def test_all_functions_importable(self):
        """All public functions should be importable."""
        from shiny.ui._html_deps_shinyverse import (
            components_dependencies,
            fill_dependency,
        )

        assert callable(fill_dependency)
        assert callable(components_dependencies)
