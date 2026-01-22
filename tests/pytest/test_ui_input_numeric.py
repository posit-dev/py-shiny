"""Tests for shiny/ui/_input_numeric.py"""

from __future__ import annotations

from unittest.mock import patch

from htmltools import Tag

from shiny.ui._input_numeric import input_numeric


class TestInputNumeric:
    """Tests for input_numeric function."""

    def test_input_numeric_basic(self) -> None:
        """Test basic numeric input creation."""
        result = input_numeric("num", "Enter number", 50)
        assert isinstance(result, Tag)
        html = str(result)
        assert "num" in html
        assert "Enter number" in html
        assert "50" in html

    def test_input_numeric_min_max(self) -> None:
        """Test numeric input with min and max."""
        result = input_numeric("num", "Number", 50, min=0, max=100)
        html = str(result)
        assert 'min="0"' in html
        assert 'max="100"' in html

    def test_input_numeric_step(self) -> None:
        """Test numeric input with step."""
        result = input_numeric("num", "Number", 10, step=5)
        html = str(result)
        assert 'step="5"' in html

    def test_input_numeric_width(self) -> None:
        """Test numeric input with width."""
        result = input_numeric("num", "Number", 10, width="300px")
        html = str(result)
        assert "300px" in html

    def test_input_numeric_update_on_blur(self) -> None:
        """Test numeric input with update_on='blur'."""
        result = input_numeric("num", "Number", 10, update_on="blur")
        html = str(result)
        assert "blur" in html

    def test_input_numeric_has_correct_type(self) -> None:
        """Test numeric input has type='number'."""
        result = input_numeric("num", "Number", 0)
        html = str(result)
        assert 'type="number"' in html

    def test_input_numeric_bookmark_restore(self) -> None:
        """Test numeric input uses bookmark restore."""
        with patch("shiny.ui._input_numeric.restore_input", return_value=999):
            result = input_numeric("num", "Number", 10)
            html = str(result)
            assert "999" in html
