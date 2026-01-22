"""Tests for shiny._versions module."""

from shiny._versions import (
    bootstrap,
    bslib,
    htmltools,
    requirejs,
    shiny_html_deps,
)


class TestVersions:
    """Tests for version strings."""

    def test_shiny_html_deps_is_string(self):
        """Test shiny_html_deps is a version string."""
        assert isinstance(shiny_html_deps, str)
        assert len(shiny_html_deps) > 0
        # Version should contain at least one dot
        assert "." in shiny_html_deps

    def test_bslib_is_string(self):
        """Test bslib is a version string."""
        assert isinstance(bslib, str)
        assert len(bslib) > 0
        assert "." in bslib

    def test_htmltools_is_string(self):
        """Test htmltools is a version string."""
        assert isinstance(htmltools, str)
        assert len(htmltools) > 0
        assert "." in htmltools

    def test_bootstrap_is_string(self):
        """Test bootstrap is a version string."""
        assert isinstance(bootstrap, str)
        assert len(bootstrap) > 0
        assert "." in bootstrap

    def test_requirejs_is_string(self):
        """Test requirejs is a version string."""
        assert isinstance(requirejs, str)
        assert len(requirejs) > 0
        assert "." in requirejs

    def test_bootstrap_version_5(self):
        """Test bootstrap is version 5.x."""
        assert bootstrap.startswith("5")
