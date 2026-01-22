"""Tests for shiny/express/__init__.py module."""

import shiny.express as express


class TestExpressModule:
    """Tests for express module."""

    def test_express_module_exists(self):
        """Test express module exists."""
        assert express is not None

    def test_express_has_ui(self):
        """Test express has ui attribute."""
        assert hasattr(express, "ui")

    def test_express_has_input(self):
        """Test express has input attribute."""
        assert hasattr(express, "input")

    def test_express_has_output(self):
        """Test express has output attribute."""
        assert hasattr(express, "output")

    def test_express_has_session(self):
        """Test express has session attribute."""
        assert hasattr(express, "session")

    def test_express_has_render(self):
        """Test express has render attribute."""
        assert hasattr(express, "render")


class TestExpressDecorators:
    """Tests for express decorators."""

    def test_expressify_exists(self):
        """Test expressify exists in express."""
        assert hasattr(express, "expressify")
