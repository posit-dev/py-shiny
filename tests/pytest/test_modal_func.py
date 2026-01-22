from htmltools import Tag, tags

from shiny.ui._modal import modal, modal_button


class TestModalButton:
    """Tests for the modal_button function."""

    def test_modal_button_basic(self):
        """Test basic modal button creation."""
        result = modal_button("Close")

        assert isinstance(result, Tag)
        assert result.name == "button"
        result_str = str(result)
        assert "Close" in result_str
        assert "btn" in result_str

    def test_modal_button_with_icon(self):
        """Test modal button with icon."""
        icon = tags.i(class_="fa fa-times")
        result = modal_button("Close", icon=icon)

        result_str = str(result)
        assert "Close" in result_str
        assert "fa-times" in result_str

    def test_modal_button_dismiss_attributes(self):
        """Test that modal button has dismiss attributes."""
        result = modal_button("Dismiss")

        result_str = str(result)
        # Should have both BS4 and BS5 dismiss attributes
        assert "data-dismiss" in result_str or "data-bs-dismiss" in result_str

    def test_modal_button_custom_class(self):
        """Test modal button with custom class."""
        result = modal_button("OK", class_="btn-primary")

        result_str = str(result)
        assert "btn-primary" in result_str

    def test_modal_button_type_attribute(self):
        """Test modal button has correct type."""
        result = modal_button("Close")

        assert result.attrs.get("type") == "button"


class TestModal:
    """Tests for the modal function."""

    def test_modal_basic(self):
        """Test basic modal creation."""
        result = modal("Modal content")

        assert isinstance(result, Tag)
        result_str = str(result)
        assert "modal" in result_str
        assert "Modal content" in result_str

    def test_modal_with_title(self):
        """Test modal with title."""
        result = modal("Content", title="My Modal Title")

        result_str = str(result)
        assert "My Modal Title" in result_str
        assert "modal-title" in result_str

    def test_modal_size_small(self):
        """Test modal with small size."""
        result = modal("Content", size="s")

        result_str = str(result)
        assert "modal-sm" in result_str

    def test_modal_size_large(self):
        """Test modal with large size."""
        result = modal("Content", size="l")

        result_str = str(result)
        assert "modal-lg" in result_str

    def test_modal_size_extra_large(self):
        """Test modal with extra large size."""
        result = modal("Content", size="xl")

        result_str = str(result)
        assert "modal-xl" in result_str

    def test_modal_size_medium(self):
        """Test modal with medium size (default)."""
        result = modal("Content", size="m")

        result_str = str(result)
        # Medium should not add extra size class
        assert "modal-sm" not in result_str
        assert "modal-lg" not in result_str
        assert "modal-xl" not in result_str

    def test_modal_easy_close_true(self):
        """Test modal with easy_close enabled."""
        result = modal("Content", easy_close=True)

        result_str = str(result)
        # When easy_close is True, backdrop should not be 'static'
        assert 'data-backdrop="static"' not in result_str

    def test_modal_easy_close_false(self):
        """Test modal with easy_close disabled (default)."""
        result = modal("Content", easy_close=False)

        result_str = str(result)
        # When easy_close is False, backdrop should be 'static'
        assert "static" in result_str

    def test_modal_fade_true(self):
        """Test modal with fade animation (default)."""
        result = modal("Content", fade=True)

        result_str = str(result)
        assert "fade" in result_str

    def test_modal_fade_false(self):
        """Test modal without fade animation."""
        result = modal("Content", fade=False)

        result_str = str(result)
        # Should have modal class but not fade
        assert "modal" in result_str
        assert "modal fade" not in result_str

    def test_modal_custom_footer(self):
        """Test modal with custom footer."""
        custom_footer = tags.div(
            modal_button("Cancel"),
            tags.button("Save", class_="btn btn-primary"),
        )
        result = modal("Content", footer=custom_footer)

        result_str = str(result)
        assert "Cancel" in result_str
        assert "Save" in result_str

    def test_modal_no_footer(self):
        """Test modal with no footer."""
        result = modal("Content", footer=None)

        result_str = str(result)
        assert "modal-body" in result_str
        # Footer div should not be present when footer=None
        # The default footer with "Dismiss" should not appear
        assert "Dismiss" not in result_str

    def test_modal_default_footer(self):
        """Test modal with default footer (Dismiss button)."""
        result = modal("Content")

        result_str = str(result)
        assert "Dismiss" in result_str
        assert "modal-footer" in result_str

    def test_modal_multiple_content(self):
        """Test modal with multiple content elements."""
        result = modal(
            tags.p("Paragraph 1"),
            tags.p("Paragraph 2"),
            tags.p("Paragraph 3"),
        )

        result_str = str(result)
        assert "Paragraph 1" in result_str
        assert "Paragraph 2" in result_str
        assert "Paragraph 3" in result_str

    def test_modal_with_kwargs(self):
        """Test modal with custom HTML attributes."""
        result = modal("Content", class_="custom-modal")

        result_str = str(result)
        assert "custom-modal" in result_str

    def test_modal_id(self):
        """Test that modal has shiny-modal id."""
        result = modal("Content")

        assert result.attrs.get("id") == "shiny-modal"

    def test_modal_includes_script(self):
        """Test that modal includes initialization script."""
        result = modal("Content")

        result_str = str(result)
        assert "script" in result_str
        assert "bootstrap" in result_str or "modal" in result_str

    def test_modal_structure(self):
        """Test modal has correct structure."""
        result = modal("Content", title="Title")

        result_str = str(result)
        # Should have modal-dialog and modal-content structure
        assert "modal-dialog" in result_str
        assert "modal-content" in result_str
        assert "modal-body" in result_str
        assert "modal-header" in result_str
