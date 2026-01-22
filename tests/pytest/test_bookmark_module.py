"""Tests for shiny.bookmark module."""

from shiny.bookmark import (
    RestoreContext,
    Unserializable,
    input_bookmark_button,
    serializer_unserializable,
)


class TestInputBookmarkButton:
    """Tests for the input_bookmark_button function."""

    def test_basic_bookmark_button(self):
        """Test creating a basic bookmark button."""
        result = input_bookmark_button()
        html = str(result)

        assert "Bookmark" in html
        assert 'id="._bookmark_"' in html

    def test_bookmark_button_custom_label(self):
        """Test bookmark button with custom label."""
        result = input_bookmark_button(label="Share")
        html = str(result)

        assert "Share" in html

    def test_bookmark_button_custom_id(self):
        """Test bookmark button with custom id."""
        result = input_bookmark_button(id="my_bookmark")
        html = str(result)

        assert 'id="my_bookmark"' in html

    def test_bookmark_button_with_width(self):
        """Test bookmark button with custom width."""
        result = input_bookmark_button(width="200px")
        html = str(result)

        assert "200px" in html

    def test_bookmark_button_disabled(self):
        """Test bookmark button with disabled state."""
        result = input_bookmark_button(disabled=True)
        html = str(result)

        assert "disabled" in html

    def test_bookmark_button_custom_title(self):
        """Test bookmark button with custom title."""
        result = input_bookmark_button(title="Share this app state")
        html = str(result)

        assert "Share this app state" in html


class TestUnserializable:
    """Tests for the Unserializable class."""

    def test_unserializable_creation(self):
        """Test creating Unserializable instance."""
        obj = Unserializable()
        assert obj is not None

    def test_serializer_unserializable_exists(self):
        """Test that serializer_unserializable exists."""
        assert serializer_unserializable is not None


class TestRestoreContext:
    """Tests for the RestoreContext class."""

    def test_restore_context_class_exists(self):
        """Test that RestoreContext class exists."""
        assert RestoreContext is not None
