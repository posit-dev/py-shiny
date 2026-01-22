"""Tests for shiny/express/expressify_decorator/__init__.py module."""

from shiny.express.expressify_decorator import expressify


class TestExpressifyDecoratorInit:
    """Tests for expressify_decorator __init__ exports."""

    def test_expressify_exported(self):
        """Test expressify is exported."""
        assert expressify is not None

    def test_expressify_is_callable(self):
        """Test expressify is callable."""
        assert callable(expressify)


class TestExpressifyExport:
    """Tests for expressify export."""

    def test_expressify_from_express(self):
        """Test expressify can be imported from express."""
        from shiny.express import expressify as exp_expressify

        assert exp_expressify is not None
