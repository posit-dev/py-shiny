"""Tests for shiny/express/_module.py module."""

from shiny.express._module import module


class TestModule:
    """Tests for module decorator."""

    def test_module_is_callable(self):
        """Test module is callable."""
        assert callable(module)


class TestModuleExported:
    """Tests for module export."""

    def test_module_exported_from_express(self):
        """Test module is exported from shiny.express."""
        from shiny import express

        assert hasattr(express, "module")
        assert callable(express.module)
