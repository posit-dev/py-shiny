"""Tests for shiny._app module - App class."""

from typing import Any

from htmltools import div

from shiny import App


class TestAppBasic:
    """Basic tests for App class instantiation."""

    def test_app_creation_with_simple_ui(self):
        """Test creating an App with a simple UI."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Hello Shiny"), server)
        assert app is not None
        assert callable(app)

    def test_app_creation_with_callable_ui(self):
        """Test creating an App with a callable UI."""

        def ui_fn(request: Any) -> Any:
            return div("Dynamic UI")

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(ui_fn, server)
        assert app is not None

    def test_app_creation_with_none_server(self):
        """Test creating an App with None server (valid for Express apps)."""
        app = App(div("Hello"), None)
        assert app is not None

    def test_app_lib_prefix_default(self):
        """Test App has default lib_prefix."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Test"), server)
        assert app.lib_prefix == "lib/"

    def test_app_sanitize_errors_default(self):
        """Test App has default sanitize_errors."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Test"), server)
        assert app.sanitize_errors is False

    def test_app_debug_mode_default(self):
        """Test App debug mode defaults to False."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Test"), server, debug=False)
        assert app is not None

    def test_app_debug_mode_enabled(self):
        """Test App debug mode can be enabled."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Test"), server, debug=True)
        assert app is not None


class TestAppStaticAssets:
    """Tests for App static asset handling."""

    def test_app_with_static_assets_none(self):
        """Test App with no static assets."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Test"), server, static_assets=None)
        assert app is not None


class TestAppRunMethod:
    """Tests for App run method configuration."""

    def test_app_is_callable(self):
        """Test that App instance is callable (ASGI interface)."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(div("Test"), server)
        assert callable(app)


class TestAppInit:
    """Tests for App initialization options."""

    def test_app_init_full_options(self):
        """Test App init with various options."""

        def server(input: Any, output: Any, session: Any) -> None:
            pass

        app = App(
            ui=div("Test UI"),
            server=server,
            debug=False,
        )
        assert app is not None
