"""Tests for shiny.ui text input modules."""

from htmltools import Tag

from shiny.ui._input_password import input_password
from shiny.ui._input_text import input_text, input_text_area


class TestInputText:
    """Tests for input_text function."""

    def test_input_text_basic(self) -> None:
        """Test basic input_text creation."""
        result = input_text("my_text", "Enter text:")
        assert isinstance(result, Tag)

    def test_input_text_has_id(self) -> None:
        """Test input_text has correct id."""
        result = input_text("text_id", "Label")
        html = str(result)
        assert "text_id" in html

    def test_input_text_with_label(self) -> None:
        """Test input_text with label."""
        result = input_text("text", "Enter your name:")
        html = str(result)
        assert "Enter your name:" in html

    def test_input_text_with_value(self) -> None:
        """Test input_text with initial value."""
        result = input_text("text", "Label", value="initial")
        html = str(result)
        assert "initial" in html

    def test_input_text_with_placeholder(self) -> None:
        """Test input_text with placeholder."""
        result = input_text("text", "Label", placeholder="Type here...")
        html = str(result)
        assert "placeholder" in html

    def test_input_text_with_width(self) -> None:
        """Test input_text with width parameter."""
        result = input_text("text", "Label", width="200px")
        html = str(result)
        assert "text" in html


class TestInputTextArea:
    """Tests for input_text_area function."""

    def test_input_text_area_basic(self) -> None:
        """Test basic input_text_area creation."""
        result = input_text_area("my_textarea", "Enter text:")
        assert isinstance(result, Tag)

    def test_input_text_area_has_id(self) -> None:
        """Test input_text_area has correct id."""
        result = input_text_area("textarea_id", "Label")
        html = str(result)
        assert "textarea_id" in html

    def test_input_text_area_with_label(self) -> None:
        """Test input_text_area with label."""
        result = input_text_area("textarea", "Enter description:")
        html = str(result)
        assert "Enter description:" in html

    def test_input_text_area_with_value(self) -> None:
        """Test input_text_area with initial value."""
        result = input_text_area("textarea", "Label", value="initial text")
        html = str(result)
        assert "initial text" in html

    def test_input_text_area_with_placeholder(self) -> None:
        """Test input_text_area with placeholder."""
        result = input_text_area("textarea", "Label", placeholder="Enter here...")
        html = str(result)
        assert "placeholder" in html

    def test_input_text_area_with_width(self) -> None:
        """Test input_text_area with width parameter."""
        result = input_text_area("textarea", "Label", width="400px")
        html = str(result)
        assert "textarea" in html

    def test_input_text_area_with_height(self) -> None:
        """Test input_text_area with height parameter."""
        result = input_text_area("textarea", "Label", height="200px")
        html = str(result)
        assert "textarea" in html

    def test_input_text_area_with_rows(self) -> None:
        """Test input_text_area with rows parameter."""
        result = input_text_area("textarea", "Label", rows=5)
        html = str(result)
        assert "textarea" in html

    def test_input_text_area_autoresize(self) -> None:
        """Test input_text_area with autoresize."""
        result = input_text_area("textarea", "Label", autoresize=True)
        html = str(result)
        assert "textarea" in html


class TestInputPassword:
    """Tests for input_password function."""

    def test_input_password_basic(self) -> None:
        """Test basic input_password creation."""
        result = input_password("my_password", "Password:")
        assert isinstance(result, Tag)

    def test_input_password_has_id(self) -> None:
        """Test input_password has correct id."""
        result = input_password("password_id", "Label")
        html = str(result)
        assert "password_id" in html

    def test_input_password_with_label(self) -> None:
        """Test input_password with label."""
        result = input_password("password", "Enter password:")
        html = str(result)
        assert "Enter password:" in html

    def test_input_password_type_attribute(self) -> None:
        """Test input_password has type=password."""
        result = input_password("password", "Label")
        html = str(result)
        assert 'type="password"' in html

    def test_input_password_with_placeholder(self) -> None:
        """Test input_password with placeholder."""
        result = input_password("password", "Label", placeholder="Enter password")
        html = str(result)
        assert "placeholder" in html

    def test_input_password_with_width(self) -> None:
        """Test input_password with width parameter."""
        result = input_password("password", "Label", width="250px")
        html = str(result)
        assert "password" in html
