"""Tests for shiny.html_dependencies module."""

from htmltools import HTMLDependency

from shiny.html_dependencies import jquery_deps, require_deps, shiny_deps


class TestShinyDeps:
    """Tests for shiny_deps function."""

    def test_shiny_deps_returns_list(self) -> None:
        """Test shiny_deps returns a list."""
        result = shiny_deps()
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_shiny_deps_contains_html_dependencies(self) -> None:
        """Test shiny_deps contains HTMLDependency objects."""
        result = shiny_deps()
        assert all(isinstance(dep, HTMLDependency) for dep in result)

    def test_shiny_deps_with_css(self) -> None:
        """Test shiny_deps with include_css=True (default)."""
        result = shiny_deps(include_css=True)
        assert len(result) >= 1

    def test_shiny_deps_without_css(self) -> None:
        """Test shiny_deps with include_css=False."""
        result = shiny_deps(include_css=False)
        assert len(result) >= 1

    def test_shiny_deps_has_shiny_dep(self) -> None:
        """Test shiny_deps includes shiny dependency."""
        result = shiny_deps()
        names = [dep.name for dep in result]
        assert "shiny" in names


class TestJqueryDeps:
    """Tests for jquery_deps function."""

    def test_jquery_deps_returns_dependency(self) -> None:
        """Test jquery_deps returns HTMLDependency."""
        result = jquery_deps()
        assert isinstance(result, HTMLDependency)

    def test_jquery_deps_name(self) -> None:
        """Test jquery_deps has correct name."""
        result = jquery_deps()
        assert result.name == "jquery"

    def test_jquery_deps_has_version(self) -> None:
        """Test jquery_deps has version."""
        result = jquery_deps()
        assert result.version is not None
        # Version is a Version object, convert to string to check
        assert str(result.version).startswith("3")


class TestRequireDeps:
    """Tests for require_deps function."""

    def test_require_deps_returns_dependency(self) -> None:
        """Test require_deps returns HTMLDependency."""
        result = require_deps()
        assert isinstance(result, HTMLDependency)

    def test_require_deps_name(self) -> None:
        """Test require_deps has correct name."""
        result = require_deps()
        assert result.name == "requirejs"

    def test_require_deps_has_version(self) -> None:
        """Test require_deps has version."""
        result = require_deps()
        assert result.version is not None
