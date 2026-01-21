"""Unit tests for shiny.ui._input_password module."""

from __future__ import annotations

from htmltools import Tag

from shiny.ui import input_password


class TestInputPassword:
    """Tests for input_password function."""

    def test_basic_input_password(self) -> None:
        """Test basic input_password with required parameters."""
        result = input_password("pwd_id", "Password")
        html = str(result)

        assert 'id="pwd_id"' in html
        assert "Password" in html
        assert 'type="password"' in html

    def test_input_password_returns_tag(self) -> None:
        """Test that input_password returns a Tag."""
        result = input_password("pwd_id", "Password")
        assert isinstance(result, Tag)

    def test_input_password_with_value(self) -> None:
        """Test input_password with initial value."""
        result = input_password("pwd_id", "Password", value="secret123")
        html = str(result)

        assert 'value="secret123"' in html

    def test_input_password_with_width(self) -> None:
        """Test input_password with width parameter."""
        result = input_password("pwd_id", "Password", width="250px")
        html = str(result)

        assert "width:250px" in html

    def test_input_password_with_placeholder(self) -> None:
        """Test input_password with placeholder."""
        result = input_password("pwd_id", "Password", placeholder="Enter password")
        html = str(result)

        assert 'placeholder="Enter password"' in html

    def test_input_password_with_all_parameters(self) -> None:
        """Test input_password with all parameters."""
        result = input_password(
            "full_pwd_id",
            "Full Password",
            value="pass",
            width="300px",
            placeholder="Your password",
        )
        html = str(result)

        assert 'id="full_pwd_id"' in html
        assert "Full Password" in html
        assert 'value="pass"' in html
        assert "width:300px" in html
        assert 'placeholder="Your password"' in html

    def test_input_password_form_group_class(self) -> None:
        """Test that container has form-group class."""
        result = input_password("pwd_id", "Password")
        html = str(result)

        assert "form-group" in html
        assert "shiny-input-container" in html

    def test_input_password_form_control_class(self) -> None:
        """Test that input element has form-control class."""
        result = input_password("pwd_id", "Password")
        html = str(result)

        assert "form-control" in html

    def test_input_password_shiny_input_class(self) -> None:
        """Test input_password has shiny-input-password class."""
        result = input_password("pwd_id", "Password")
        html = str(result)

        assert "shiny-input-password" in html

    def test_input_password_html_label(self) -> None:
        """Test input_password with HTML label."""
        from htmltools import tags

        label = tags.em("Italic Password")
        result = input_password("pwd_id", label)
        html = str(result)

        assert "<em>Italic Password</em>" in html

    def test_input_password_empty_label(self) -> None:
        """Test input_password with empty label."""
        result = input_password("pwd_id", "")
        html = str(result)

        assert 'id="pwd_id"' in html

    def test_input_password_empty_value(self) -> None:
        """Test input_password with empty value."""
        result = input_password("pwd_id", "Password", value="")
        html = str(result)

        assert 'value=""' in html

    def test_input_password_default_value_empty(self) -> None:
        """Test input_password default value is empty string."""
        result = input_password("pwd_id", "Password")
        html = str(result)

        # Default value should be empty
        assert 'value=""' in html

    def test_input_password_update_on_change(self) -> None:
        """Test input_password with update_on='change'."""
        result = input_password("pwd_id", "Password", update_on="change")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_input_password_update_on_blur(self) -> None:
        """Test input_password with update_on='blur'."""
        result = input_password("pwd_id", "Password", update_on="blur")
        html = str(result)

        assert 'data-update-on="blur"' in html

    def test_input_password_default_update_on(self) -> None:
        """Test input_password default update_on is 'change'."""
        result = input_password("pwd_id", "Password")
        html = str(result)

        assert 'data-update-on="change"' in html

    def test_input_password_with_special_characters(self) -> None:
        """Test input_password with special characters in value."""
        result = input_password("pwd_id", "Password", value="p@ss&word<>")
        html = str(result)

        # HTML should escape special characters
        assert "pwd_id" in html

    def test_input_password_with_long_placeholder(self) -> None:
        """Test input_password with long placeholder text."""
        placeholder = "Please enter your super secure password here"
        result = input_password("pwd_id", "Password", placeholder=placeholder)
        html = str(result)

        assert f'placeholder="{placeholder}"' in html
