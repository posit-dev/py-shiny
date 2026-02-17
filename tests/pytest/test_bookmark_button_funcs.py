"""Tests for shiny.bookmark._button module"""

from htmltools import Tag

from shiny.bookmark._button import BOOKMARK_ID, input_bookmark_button


class TestInputBookmarkButton:
    """Test input_bookmark_button function"""

    def test_default_button(self):
        """Test creating bookmark button with defaults"""
        result = input_bookmark_button()
        assert isinstance(result, Tag)
        assert result.name == "button"

    def test_button_has_default_id(self):
        """Test bookmark button has default id"""
        result = input_bookmark_button()
        assert result.attrs.get("id") == BOOKMARK_ID

    def test_default_label(self):
        """Test bookmark button has default label"""
        result = input_bookmark_button()
        html = str(result)
        assert "Bookmark..." in html

    def test_custom_label(self):
        """Test bookmark button with custom label"""
        result = input_bookmark_button(label="Save State")
        html = str(result)
        assert "Save State" in html

    def test_custom_id(self):
        """Test bookmark button with custom id"""
        result = input_bookmark_button(id="custom_bookmark")
        assert result.attrs.get("id") == "custom_bookmark"

    def test_custom_width(self):
        """Test bookmark button with custom width"""
        result = input_bookmark_button(width="200px")
        html = str(result)
        assert "width" in html or "200px" in str(result.attrs)

    def test_disabled_button(self):
        """Test disabled bookmark button"""
        result = input_bookmark_button(disabled=True)
        assert result.attrs.get("disabled") == "disabled" or "disabled" in str(result)

    def test_custom_title(self):
        """Test bookmark button with custom title"""
        result = input_bookmark_button(title="Custom tooltip")
        assert result.attrs.get("title") == "Custom tooltip"

    def test_default_title(self):
        """Test bookmark button has default title"""
        result = input_bookmark_button()
        expected_title = "Bookmark this application's state and get a URL for sharing."
        assert result.attrs.get("title") == expected_title

    def test_button_is_action_button(self):
        """Test bookmark button is an action button"""
        result = input_bookmark_button()
        # Action buttons have specific class
        html = str(result)
        assert "action-button" in html or "btn" in html

    def test_with_kwargs(self):
        """Test bookmark button with additional attributes"""
        result = input_bookmark_button(class_="custom-class")
        html = str(result)
        assert "custom-class" in html


class TestBookmarkId:
    """Test BOOKMARK_ID constant"""

    def test_bookmark_id_value(self):
        """Test BOOKMARK_ID has expected value"""
        assert BOOKMARK_ID == "._bookmark_"

    def test_bookmark_id_is_string(self):
        """Test BOOKMARK_ID is a string"""
        assert isinstance(BOOKMARK_ID, str)

    def test_bookmark_id_starts_with_dot(self):
        """Test BOOKMARK_ID starts with dot (special naming)"""
        assert BOOKMARK_ID.startswith(".")
