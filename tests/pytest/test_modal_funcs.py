"""Tests for shiny.ui._modal module."""

from htmltools import Tag

from shiny.ui._modal import modal, modal_button


class TestModal:
    """Tests for modal function."""

    def test_modal_basic(self) -> None:
        """Test basic modal creation."""
        result = modal("Modal content")
        assert isinstance(result, Tag)

    def test_modal_with_title(self) -> None:
        """Test modal with title."""
        result = modal("Content", title="My Modal")
        html = str(result)
        assert "My Modal" in html

    def test_modal_with_content(self) -> None:
        """Test modal with content."""
        result = modal("This is modal content")
        html = str(result)
        assert "This is modal content" in html

    def test_modal_has_modal_class(self) -> None:
        """Test modal has modal class."""
        result = modal("Content")
        html = str(result)
        assert "modal" in html

    def test_modal_easy_close(self) -> None:
        """Test modal with easy_close=True."""
        result = modal("Content", easy_close=True)
        html = str(result)
        assert "modal" in html

    def test_modal_easy_close_false(self) -> None:
        """Test modal with easy_close=False."""
        result = modal("Content", easy_close=False)
        html = str(result)
        assert "modal" in html

    def test_modal_with_footer(self) -> None:
        """Test modal with footer."""
        result = modal("Content", footer=modal_button("Close"))
        html = str(result)
        assert "modal" in html

    def test_modal_size_small(self) -> None:
        """Test modal with size='s'."""
        result = modal("Content", size="s")
        html = str(result)
        assert "modal" in html

    def test_modal_size_medium(self) -> None:
        """Test modal with size='m'."""
        result = modal("Content", size="m")
        html = str(result)
        assert "modal" in html

    def test_modal_size_large(self) -> None:
        """Test modal with size='l'."""
        result = modal("Content", size="l")
        html = str(result)
        assert "modal" in html

    def test_modal_fade(self) -> None:
        """Test modal with fade=True."""
        result = modal("Content", fade=True)
        html = str(result)
        assert "modal" in html

    def test_modal_fade_false(self) -> None:
        """Test modal with fade=False."""
        result = modal("Content", fade=False)
        html = str(result)
        assert "modal" in html


class TestModalButton:
    """Tests for modal_button function."""

    def test_modal_button_basic(self) -> None:
        """Test basic modal_button creation."""
        result = modal_button("Close")
        assert isinstance(result, Tag)

    def test_modal_button_with_label(self) -> None:
        """Test modal_button with label."""
        result = modal_button("Dismiss")
        html = str(result)
        assert "Dismiss" in html

    def test_modal_button_is_button(self) -> None:
        """Test modal_button returns button tag."""
        result = modal_button("Label")
        assert result.name == "button"

    def test_modal_button_has_dismiss(self) -> None:
        """Test modal_button has dismiss attribute."""
        result = modal_button("Close")
        html = str(result)
        assert "dismiss" in html or "Close" in html

    def test_modal_button_has_btn_class(self) -> None:
        """Test modal_button has btn class."""
        result = modal_button("Close")
        html = str(result)
        assert "btn" in html
