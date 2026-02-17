"""Tests for shiny/playwright/expect/__init__.py module."""

import shiny.playwright.expect as expect


class TestExpectExports:
    """Tests for expect module exports."""

    def test_expect_has_expect_to_have_class(self):
        """Test expect has expect_to_have_class."""
        assert hasattr(expect, "expect_to_have_class")


class TestExpectAll:
    """Tests for __all__ exports."""

    def test_all_is_list(self):
        """Test __all__ is a list."""
        assert isinstance(expect.__all__, list)

    def test_all_contains_expect_to_have_class(self):
        """Test __all__ contains expect_to_have_class."""
        assert "expect_to_have_class" in expect.__all__
