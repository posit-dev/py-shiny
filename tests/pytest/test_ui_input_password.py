"""Tests for shiny/ui/_input_password.py"""

from __future__ import annotations

from htmltools import Tag

from shiny.ui._input_password import input_password


class TestInputPassword:
    """Tests for input_password function."""

    def test_input_password_basic(self) -> None:
        """Test basic password input creation."""
        result = input_password("pwd", "Password")
        assert isinstance(result, Tag)
        html = str(result)
        assert "pwd" in html
        assert "Password" in html

    def test_input_password_with_value(self) -> None:
        """Test password input with initial value."""
        result = input_password("pwd", "Password", value="secret")
        html = str(result)
        assert 'value="secret"' in html

    def test_input_password_with_width(self) -> None:
        """Test password input with width."""
        result = input_password("pwd", "Password", width="250px")
        html = str(result)
        assert "250px" in html

    def test_input_password_with_placeholder(self) -> None:
        """Test password input with placeholder."""
        result = input_password("pwd", "Password", placeholder="Enter password...")
        html = str(result)
        assert "Enter password..." in html

    def test_input_password_update_on_blur(self) -> None:
        """Test password input with update_on='blur'."""
        result = input_password("pwd", "Password", update_on="blur")
        html = str(result)
        assert "blur" in html

    def test_input_password_has_correct_type(self) -> None:
        """Test password input has type='password'."""
        result = input_password("pwd", "Password")
        html = str(result)
        assert 'type="password"' in html

    def test_input_password_has_form_control_class(self) -> None:
        """Test password input has form-control class."""
        result = input_password("pwd", "Password")
        html = str(result)
        assert "form-control" in html
