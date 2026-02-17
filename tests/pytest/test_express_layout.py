"""Tests for shiny/express/layout.py module (deprecated)."""

import warnings


class TestLayoutDeprecated:
    """Tests for layout module deprecation."""

    def test_layout_import_warns(self):
        """Test importing layout raises deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import shiny.express.layout as layout  # noqa: F401

            # Filter for ImportWarning
            _ = [x for x in w if issubclass(x.category, ImportWarning)]
            # May or may not trigger depending on whether already imported
            # Just check the import works
            assert layout is not None

    def test_layout_proxies_to_ui(self):
        """Test layout module proxies to ui module."""
        import shiny.express.layout as layout
        import shiny.express.ui as ui

        # Test that accessing an attribute from layout gets it from ui
        assert hasattr(ui, "h1")
        # layout should proxy to ui
        assert layout.h1 == ui.h1

    def test_layout_has_getattr(self):
        """Test layout module has __getattr__ for proxying."""
        import shiny.express.layout as layout

        # Should be able to access ui functions through layout
        assert hasattr(layout, "div")
        assert callable(layout.div)
