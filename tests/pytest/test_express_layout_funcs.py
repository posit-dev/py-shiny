"""Tests for shiny.express.layout module (deprecated)"""

import warnings


class TestExpressLayout:
    """Test deprecated express.layout module"""

    def test_import_warning(self):
        """Test importing express.layout emits deprecation warning"""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            # Force reimport
            import importlib

            import shiny.express.layout

            importlib.reload(shiny.express.layout)

            # Check that a warning was issued
            assert len(w) >= 1
            # Find the deprecation warning
            deprecation_warnings = [
                x for x in w if "deprecated" in str(x.message).lower()
            ]
            assert len(deprecation_warnings) >= 1

    def test_getattr_forwards_to_ui(self):
        """Test __getattr__ forwards to ui module"""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ImportWarning)
            from shiny.express import layout

            # Should be able to access ui functions through layout
            # These should be the same as shiny.express.ui functions
            assert hasattr(layout, "sidebar")
            assert hasattr(layout, "card")
