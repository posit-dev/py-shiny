"""Tests for shiny/http_staticfiles.py module."""


class TestHttpStaticFiles:
    """Tests for http_staticfiles module."""

    def test_module_exists(self):
        """Test http_staticfiles module can be imported."""
        from shiny import http_staticfiles

        assert http_staticfiles is not None

    def test_staticfileshandler_class_exists(self):
        """Test StaticFilesHandler class exists."""
        from shiny.http_staticfiles import StaticFiles

        assert StaticFiles is not None
