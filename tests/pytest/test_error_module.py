"""Tests for shiny._error module."""

from shiny._error import ErrorMiddleware


class TestErrorMiddleware:
    """Tests for ErrorMiddleware class."""

    def test_init(self) -> None:
        """Test ErrorMiddleware initialization."""

        async def dummy_app(scope, receive, send):
            pass

        middleware = ErrorMiddleware(dummy_app)
        assert middleware.app is dummy_app

    def test_has_app_attribute(self) -> None:
        """Test ErrorMiddleware has app attribute."""

        async def dummy_app(scope, receive, send):
            pass

        middleware = ErrorMiddleware(dummy_app)
        assert hasattr(middleware, "app")

    def test_is_callable(self) -> None:
        """Test ErrorMiddleware is callable."""

        async def dummy_app(scope, receive, send):
            pass

        middleware = ErrorMiddleware(dummy_app)
        assert callable(middleware)
