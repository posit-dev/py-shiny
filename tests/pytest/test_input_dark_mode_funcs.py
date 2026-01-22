"""Tests for shiny.ui._input_dark_mode module."""

import pytest
from htmltools import Tag

from shiny.ui._input_dark_mode import (
    input_dark_mode,
    validate_dark_mode_option,
)


class TestInputDarkMode:
    """Tests for input_dark_mode function."""

    def test_input_dark_mode_basic(self) -> None:
        """Test basic input_dark_mode creation."""
        result = input_dark_mode()
        assert isinstance(result, Tag)
        html = str(result)
        assert "bslib-input-dark-mode" in html

    def test_input_dark_mode_with_id(self) -> None:
        """Test input_dark_mode with id."""
        # IDs can only contain letters, numbers, and underscores
        result = input_dark_mode(id="dark_mode_toggle")
        html = str(result)
        assert 'id="dark_mode_toggle"' in html

    def test_input_dark_mode_light_mode(self) -> None:
        """Test input_dark_mode with light mode."""
        result = input_dark_mode(mode="light")
        html = str(result)
        assert "bslib-input-dark-mode" in html

    def test_input_dark_mode_dark_mode(self) -> None:
        """Test input_dark_mode with dark mode."""
        result = input_dark_mode(mode="dark")
        html = str(result)
        assert "bslib-input-dark-mode" in html

    def test_input_dark_mode_with_kwargs(self) -> None:
        """Test input_dark_mode with additional attributes."""
        result = input_dark_mode(class_="my-dark-mode")
        html = str(result)
        assert "my-dark-mode" in html


class TestValidateDarkModeOption:
    """Tests for validate_dark_mode_option function."""

    def test_validate_light(self) -> None:
        """Test validate_dark_mode_option with light."""
        result = validate_dark_mode_option("light")
        assert result == "light"

    def test_validate_dark(self) -> None:
        """Test validate_dark_mode_option with dark."""
        result = validate_dark_mode_option("dark")
        assert result == "dark"

    def test_validate_invalid(self) -> None:
        """Test validate_dark_mode_option with invalid option."""
        with pytest.raises(ValueError, match="must be either 'light' or 'dark'"):
            validate_dark_mode_option("invalid")  # type: ignore
