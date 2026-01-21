"""Tests for shiny/html_dependencies.py - HTML dependency functions."""

import os
from unittest.mock import patch

from htmltools import HTMLDependency

from shiny import __version__
from shiny.html_dependencies import jquery_deps, require_deps, shiny_deps


class TestShinyDeps:
    """Tests for shiny_deps function."""

    def test_returns_list(self):
        """Test that shiny_deps returns a list."""
        deps = shiny_deps()
        assert isinstance(deps, list)

    def test_contains_html_dependencies(self):
        """Test that list contains HTMLDependency objects."""
        deps = shiny_deps()
        for dep in deps:
            assert isinstance(dep, HTMLDependency)

    def test_includes_shiny_dependency(self):
        """Test that shiny dependency is included."""
        deps = shiny_deps()
        dep_names = [dep.name for dep in deps]
        assert "shiny" in dep_names

    def test_shiny_dependency_has_correct_version(self):
        """Test that shiny dependency has correct version."""
        deps = shiny_deps()
        shiny_dep = next(d for d in deps if d.name == "shiny")
        assert str(shiny_dep.version) == __version__

    def test_includes_css_by_default(self):
        """Test that CSS is included by default."""
        deps = shiny_deps(include_css=True)
        shiny_dep = next(d for d in deps if d.name == "shiny")
        # Check that stylesheet is not None
        assert shiny_dep.stylesheet is not None

    def test_excludes_css_when_false(self):
        """Test that CSS can be excluded."""
        deps = shiny_deps(include_css=False)
        shiny_dep = next(d for d in deps if d.name == "shiny")
        # Check that stylesheet is empty or None
        assert shiny_dep.stylesheet is None or len(shiny_dep.stylesheet) == 0

    def test_includes_busy_indicators(self):
        """Test that busy indicators dependency is included."""
        deps = shiny_deps()
        # Should have at least 2 dependencies (shiny + busy_indicators)
        assert len(deps) >= 2

    def test_dev_mode_adds_devmode_dep(self):
        """Test that dev mode adds shiny-devmode dependency."""
        with patch.dict(os.environ, {"SHINY_DEV_MODE": "1"}):
            deps = shiny_deps()
            dep_names = [dep.name for dep in deps]
            assert "shiny-devmode" in dep_names

    def test_no_devmode_dep_when_not_dev_mode(self):
        """Test that devmode dep not included when not in dev mode."""
        with patch.dict(os.environ, {"SHINY_DEV_MODE": "0"}, clear=False):
            deps = shiny_deps()
            dep_names = [dep.name for dep in deps]
            assert "shiny-devmode" not in dep_names


class TestJqueryDeps:
    """Tests for jquery_deps function."""

    def test_returns_html_dependency(self):
        """Test that jquery_deps returns HTMLDependency."""
        dep = jquery_deps()
        assert isinstance(dep, HTMLDependency)

    def test_has_correct_name(self):
        """Test that dependency has correct name."""
        dep = jquery_deps()
        assert dep.name == "jquery"

    def test_has_version(self):
        """Test that dependency has version."""
        dep = jquery_deps()
        assert str(dep.version) == "3.6.0"

    def test_has_script(self):
        """Test that dependency has script."""
        dep = jquery_deps()
        assert dep.script is not None


class TestRequireDeps:
    """Tests for require_deps function."""

    def test_returns_html_dependency(self):
        """Test that require_deps returns HTMLDependency."""
        dep = require_deps()
        assert isinstance(dep, HTMLDependency)

    def test_has_correct_name(self):
        """Test that dependency has correct name."""
        dep = require_deps()
        assert dep.name == "requirejs"

    def test_has_version(self):
        """Test that dependency has version."""
        dep = require_deps()
        assert str(dep.version) == "2.3.6"

    def test_has_script(self):
        """Test that dependency has script."""
        dep = require_deps()
        assert dep.script is not None
