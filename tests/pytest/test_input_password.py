"""Tests for shiny.ui._input_password module."""

from shiny.ui import input_password


class TestInputPassword:
    """Tests for input_password function."""

    def test_input_password_basic(self):
        """Test basic input_password creation."""
        widget = input_password("password_id", "Password")
        html = str(widget)
        assert "password_id" in html
        assert "Password" in html
        assert 'type="password"' in html

    def test_input_password_with_value(self):
        """Test input_password with initial value."""
        widget = input_password("password_id", "Password", value="secret")
        html = str(widget)
        assert 'value="secret"' in html

    def test_input_password_with_width(self):
        """Test input_password with width."""
        widget = input_password("password_id", "Password", width="250px")
        html = str(widget)
        assert "250px" in html

    def test_input_password_with_placeholder(self):
        """Test input_password with placeholder."""
        widget = input_password(
            "password_id", "Password", placeholder="Enter password..."
        )
        html = str(widget)
        assert "Enter password..." in html

    def test_input_password_update_on_change(self):
        """Test input_password with update_on change."""
        widget = input_password("password_id", "Password", update_on="change")
        html = str(widget)
        assert "change" in html

    def test_input_password_update_on_blur(self):
        """Test input_password with update_on blur."""
        widget = input_password("password_id", "Password", update_on="blur")
        html = str(widget)
        assert "blur" in html

    def test_input_password_class(self):
        """Test input_password has correct CSS classes."""
        widget = input_password("password_id", "Password")
        html = str(widget)
        assert "shiny-input-password" in html
        assert "form-control" in html
        assert "shiny-input-container" in html
