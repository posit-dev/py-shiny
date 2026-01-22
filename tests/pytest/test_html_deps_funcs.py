"""Tests for shiny.html_dependencies module."""

from htmltools import HTMLDependency

from shiny.html_dependencies import shiny_deps, jquery_deps, require_deps


class TestShinyDeps:
    """Tests for shiny_deps function."""

    def test_shiny_deps_returns_list(self):
        """Test shiny_deps returns a list of dependencies."""
        deps = shiny_deps()
        assert isinstance(deps, list)
        assert len(deps) >= 1

    def test_shiny_deps_contains_html_dependency(self):
        """Test shiny_deps contains HTMLDependency objects."""
        deps = shiny_deps()
        for dep in deps:
            assert isinstance(dep, HTMLDependency)

    def test_shiny_deps_has_shiny_dependency(self):
        """Test shiny_deps includes the shiny dependency."""
        deps = shiny_deps()
        names = [dep.name for dep in deps]
        assert "shiny" in names

    def test_shiny_deps_with_css(self):
        """Test shiny_deps includes CSS by default."""
        deps = shiny_deps(include_css=True)
        shiny_dep = next(dep for dep in deps if dep.name == "shiny")
        assert shiny_dep.stylesheet is not None

    def test_shiny_deps_without_css(self):
        """Test shiny_deps can exclude CSS."""
        deps = shiny_deps(include_css=False)
        shiny_dep = next(dep for dep in deps if dep.name == "shiny")
        # Returns empty list when CSS is excluded
        assert not shiny_dep.stylesheet


class TestJqueryDeps:
    """Tests for jquery_deps function."""

    def test_jquery_deps_returns_dependency(self):
        """Test jquery_deps returns an HTMLDependency."""
        dep = jquery_deps()
        assert isinstance(dep, HTMLDependency)

    def test_jquery_deps_name(self):
        """Test jquery_deps has correct name."""
        dep = jquery_deps()
        assert dep.name == "jquery"

    def test_jquery_deps_version(self):
        """Test jquery_deps has a version."""
        dep = jquery_deps()
        assert dep.version is not None
        assert str(dep.version) != ""


class TestRequireDeps:
    """Tests for require_deps function."""

    def test_require_deps_returns_dependency(self):
        """Test require_deps returns an HTMLDependency."""
        dep = require_deps()
        assert isinstance(dep, HTMLDependency)

    def test_require_deps_name(self):
        """Test require_deps has correct name."""
        dep = require_deps()
        assert dep.name == "requirejs"

    def test_require_deps_version(self):
        """Test require_deps has a version."""
        dep = require_deps()
        assert dep.version is not None
        assert str(dep.version) != ""
