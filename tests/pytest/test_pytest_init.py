"""Tests for shiny/pytest/__init__.py module."""

import shiny.pytest as pytest_shiny


class TestPytestExports:
    """Tests for pytest module exports."""

    def test_pytest_has_create_app_fixture(self):
        """Test pytest has create_app_fixture."""
        assert hasattr(pytest_shiny, "create_app_fixture")


class TestPytestAll:
    """Tests for __all__ exports."""

    def test_all_is_tuple(self):
        """Test __all__ is a tuple."""
        assert isinstance(pytest_shiny.__all__, tuple)

    def test_all_contains_create_app_fixture(self):
        """Test __all__ contains create_app_fixture."""
        assert "create_app_fixture" in pytest_shiny.__all__
