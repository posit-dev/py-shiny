"""Tests for shiny/ui/_input_password.py - Password input."""

from htmltools import Tag

from shiny.ui import input_password


class TestInputPassword:
    """Tests for input_password function."""

    def test_input_password_returns_tag(self):
        """Test input_password returns a Tag."""
        result = input_password("pwd_id", "Password")
        assert isinstance(result, Tag)

    def test_input_password_has_correct_id(self):
        """Test input_password has correct id."""
        result = input_password("pwd_id", "Password")
        html = str(result)
        assert "pwd_id" in html

    def test_input_password_has_label(self):
        """Test input_password has label."""
        result = input_password("pwd_id", "Enter password")
        html = str(result)
        assert "Enter password" in html

    def test_input_password_has_type_password(self):
        """Test input_password has type=password."""
        result = input_password("pwd_id", "Password")
        html = str(result)
        assert 'type="password"' in html

    def test_input_password_empty_value_by_default(self):
        """Test input_password has empty value by default."""
        result = input_password("pwd_id", "Password")
        html = str(result)
        assert 'value=""' in html

    def test_input_password_with_value(self):
        """Test input_password with initial value."""
        result = input_password("pwd_id", "Password", value="secret")
        html = str(result)
        assert 'value="secret"' in html

    def test_input_password_with_width(self):
        """Test input_password with width."""
        result = input_password("pwd_id", "Password", width="300px")
        html = str(result)
        assert "300px" in html

    def test_input_password_with_placeholder(self):
        """Test input_password with placeholder."""
        result = input_password("pwd_id", "Password", placeholder="Enter your password")
        html = str(result)
        assert "Enter your password" in html


class TestInputPasswordAll:
    """Tests for __all__ exports."""

    def test_input_password_in_all(self):
        """Test input_password is in __all__."""
        from shiny.ui._input_password import __all__

        assert "input_password" in __all__
