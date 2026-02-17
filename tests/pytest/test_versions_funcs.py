"""Tests for shiny._versions module"""

from shiny._versions import (
    bootstrap,
    bslib,
    htmltools,
    requirejs,
    shiny_html_deps,
)


class TestVersionConstants:
    """Test version string constants"""

    def test_shiny_html_deps_is_string(self):
        """Test that shiny_html_deps is a string"""
        assert isinstance(shiny_html_deps, str)

    def test_shiny_html_deps_format(self):
        """Test that shiny_html_deps follows semver-like format"""
        # Should contain at least major.minor.patch
        parts = shiny_html_deps.split(".")
        assert len(parts) >= 3
        # First three parts should be numeric (possibly followed by pre-release info)
        assert parts[0].isdigit()
        assert parts[1].isdigit()
        # Third part might have .9000 suffix for dev versions

    def test_bslib_is_string(self):
        """Test that bslib is a string"""
        assert isinstance(bslib, str)

    def test_bslib_format(self):
        """Test that bslib follows version format"""
        parts = bslib.split(".")
        assert len(parts) >= 3
        assert parts[0].isdigit()

    def test_htmltools_is_string(self):
        """Test that htmltools is a string"""
        assert isinstance(htmltools, str)

    def test_htmltools_format(self):
        """Test that htmltools follows version format"""
        parts = htmltools.split(".")
        assert len(parts) >= 3
        assert parts[0].isdigit()

    def test_bootstrap_is_string(self):
        """Test that bootstrap is a string"""
        assert isinstance(bootstrap, str)

    def test_bootstrap_format(self):
        """Test that bootstrap follows semver format"""
        parts = bootstrap.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)

    def test_bootstrap_version_5(self):
        """Test that bootstrap is version 5.x"""
        assert bootstrap.startswith("5.")

    def test_requirejs_is_string(self):
        """Test that requirejs is a string"""
        assert isinstance(requirejs, str)

    def test_requirejs_format(self):
        """Test that requirejs follows semver format"""
        parts = requirejs.split(".")
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)


class TestVersionExports:
    """Test that all versions are properly exported"""

    def test_all_exports(self):
        """Test that __all__ contains expected exports"""
        from shiny import _versions

        expected = ["shiny_html_deps", "bslib", "htmltools", "bootstrap", "requirejs"]
        for name in expected:
            assert hasattr(_versions, name)

    def test_versions_are_non_empty(self):
        """Test that no version is an empty string"""
        assert len(shiny_html_deps) > 0
        assert len(bslib) > 0
        assert len(htmltools) > 0
        assert len(bootstrap) > 0
        assert len(requirejs) > 0
