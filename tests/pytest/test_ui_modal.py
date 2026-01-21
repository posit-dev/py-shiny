"""Tests for shiny/ui/_modal.py"""

from __future__ import annotations

from htmltools import Tag

from shiny.ui import modal, modal_button


class TestModalButton:
    """Tests for the modal_button function."""

    def test_basic_button(self) -> None:
        """Test creating a basic modal button."""
        result = modal_button("Close")
        assert isinstance(result, Tag)
        assert result.name == "button"
        assert "btn" in result.attrs.get("class", "")
        assert "btn-default" in result.attrs.get("class", "")
        assert result.attrs.get("type") == "button"

    def test_button_with_icon(self) -> None:
        """Test creating a button with an icon."""
        result = modal_button("Close", icon="✓")
        assert isinstance(result, Tag)

    def test_button_with_custom_attrs(self) -> None:
        """Test creating a button with custom attributes."""
        result = modal_button("Close", id="my-btn", class_="custom-class")
        assert isinstance(result, Tag)
        assert result.attrs.get("id") == "my-btn"

    def test_button_has_dismiss_attrs(self) -> None:
        """Test that button has Bootstrap dismiss attributes."""
        result = modal_button("Dismiss")
        # Should have both BS4 and BS5 dismiss attributes
        assert result.attrs.get("data-dismiss") == "modal"
        assert result.attrs.get("data-bs-dismiss") == "modal"


class TestModal:
    """Tests for the modal function."""

    def test_basic_modal(self) -> None:
        """Test creating a basic modal."""
        result = modal("Content")
        assert isinstance(result, Tag)
        assert result.name == "div"
        assert result.attrs.get("id") == "shiny-modal"
        assert "modal" in result.attrs.get("class", "")
        assert "fade" in result.attrs.get("class", "")

    def test_modal_with_title(self) -> None:
        """Test creating a modal with a title."""
        result = modal("Content", title="My Title")
        assert isinstance(result, Tag)
        # The title should be present in the rendered HTML
        rendered = str(result)
        assert "My Title" in rendered
        assert "modal-title" in rendered

    def test_modal_without_fade(self) -> None:
        """Test creating a modal without fade animation."""
        result = modal("Content", fade=False)
        assert isinstance(result, Tag)
        class_attr = result.attrs.get("class", "")
        assert "modal" in class_attr
        assert "fade" not in class_attr

    def test_modal_sizes(self) -> None:
        """Test modal with different sizes."""
        # Small modal
        small = modal("Content", size="s")
        assert "modal-sm" in str(small)

        # Large modal
        large = modal("Content", size="l")
        assert "modal-lg" in str(large)

        # Extra large modal
        xl = modal("Content", size="xl")
        assert "modal-xl" in str(xl)

        # Medium modal (default)
        medium = modal("Content", size="m")
        modal_html = str(medium)
        assert "modal-sm" not in modal_html
        assert "modal-lg" not in modal_html
        assert "modal-xl" not in modal_html

    def test_modal_easy_close(self) -> None:
        """Test modal with easy_close option."""
        # With easy_close=True, backdrop/keyboard should be None (not set)
        easy = modal("Content", easy_close=True)
        assert easy.attrs.get("data-backdrop") is None
        assert easy.attrs.get("data-keyboard") is None
        assert easy.attrs.get("data-bs-backdrop") is None
        assert easy.attrs.get("data-bs-keyboard") is None

        # With easy_close=False, backdrop should be "static"
        hard = modal("Content", easy_close=False)
        assert hard.attrs.get("data-backdrop") == "static"
        assert hard.attrs.get("data-keyboard") == "false"
        assert hard.attrs.get("data-bs-backdrop") == "static"
        assert hard.attrs.get("data-bs-keyboard") == "false"

    def test_modal_default_footer(self) -> None:
        """Test that modal has a default footer with dismiss button."""
        result = modal("Content")
        rendered = str(result)
        assert "modal-footer" in rendered
        assert "Dismiss" in rendered

    def test_modal_no_footer(self) -> None:
        """Test modal with no footer."""
        result = modal("Content", footer=None)
        rendered = str(result)
        assert "modal-footer" not in rendered

    def test_modal_custom_footer(self) -> None:
        """Test modal with custom footer."""
        custom_footer = modal_button("Save Changes")
        result = modal("Content", footer=custom_footer)
        rendered = str(result)
        assert "modal-footer" in rendered
        assert "Save Changes" in rendered

    def test_modal_multiple_children(self) -> None:
        """Test modal with multiple content elements."""
        result = modal("Paragraph 1", "Paragraph 2", "Paragraph 3")
        rendered = str(result)
        assert "Paragraph 1" in rendered
        assert "Paragraph 2" in rendered
        assert "Paragraph 3" in rendered

    def test_modal_with_kwargs(self) -> None:
        """Test modal with additional body kwargs."""
        result = modal("Content", id="body-id")
        # id should be on the modal itself, not the body
        assert result.attrs.get("id") == "shiny-modal"

    def test_modal_has_script(self) -> None:
        """Test that modal includes JavaScript for Bootstrap compatibility."""
        result = modal("Content")
        rendered = str(result)
        assert "<script>" in rendered
        assert "bootstrap.Modal" in rendered or "modal" in rendered

    def test_modal_tabindex(self) -> None:
        """Test that modal has tabindex for accessibility."""
        result = modal("Content")
        assert result.attrs.get("tabindex") == "-1"


class TestModalStructure:
    """Tests for modal DOM structure."""

    def test_modal_structure(self) -> None:
        """Test that modal has correct nested structure."""
        result = modal("Content", title="Title")
        rendered = str(result)
        # Check for required structural classes
        assert "modal-dialog" in rendered
        assert "modal-content" in rendered
        assert "modal-body" in rendered

    def test_modal_header_only_with_title(self) -> None:
        """Test that modal header only appears when title is provided."""
        with_title = modal("Content", title="My Title")
        without_title = modal("Content")

        assert "modal-header" in str(with_title)
        assert "modal-header" not in str(without_title)
