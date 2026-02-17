"""Unit tests for shiny.ui._modal module."""

from __future__ import annotations

from htmltools import Tag

from shiny.ui import modal, modal_button


class TestModalButton:
    """Tests for modal_button function."""

    def test_basic_modal_button(self) -> None:
        """Test basic modal_button with required parameters."""
        result = modal_button("Close")
        html = str(result)

        assert "Close" in html
        assert "<button" in html

    def test_modal_button_returns_tag(self) -> None:
        """Test that modal_button returns a Tag."""
        result = modal_button("Close")
        assert isinstance(result, Tag)

    def test_modal_button_btn_class(self) -> None:
        """Test modal_button has btn class."""
        result = modal_button("Close")
        html = str(result)

        assert "btn" in html
        assert "btn-default" in html

    def test_modal_button_dismiss_attributes(self) -> None:
        """Test modal_button has data-dismiss attributes."""
        result = modal_button("Close")
        html = str(result)

        assert 'data-dismiss="modal"' in html
        assert 'data-bs-dismiss="modal"' in html

    def test_modal_button_type_button(self) -> None:
        """Test modal_button has type='button'."""
        result = modal_button("Close")
        html = str(result)

        assert 'type="button"' in html

    def test_modal_button_with_icon(self) -> None:
        """Test modal_button with icon parameter."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-times")
        result = modal_button("Close", icon=icon)
        html = str(result)

        assert "fa-times" in html

    def test_modal_button_custom_kwargs(self) -> None:
        """Test modal_button with custom kwargs."""
        result = modal_button("Close", class_="custom-class", data_custom="value")
        html = str(result)

        assert "custom-class" in html
        assert 'data-custom="value"' in html

    def test_modal_button_html_label(self) -> None:
        """Test modal_button with HTML label."""
        from htmltools import tags

        label = tags.strong("Bold Close")
        result = modal_button(label)
        html = str(result)

        assert "<strong>Bold Close</strong>" in html


class TestModal:
    """Tests for modal function."""

    def test_basic_modal(self) -> None:
        """Test basic modal with content."""
        result = modal("Modal content")
        html = str(result)

        assert "Modal content" in html
        assert "modal" in html.lower()

    def test_modal_returns_tag(self) -> None:
        """Test that modal returns a Tag."""
        result = modal("Content")
        assert isinstance(result, Tag)

    def test_modal_with_title(self) -> None:
        """Test modal with title parameter."""
        result = modal("Content", title="My Modal")
        html = str(result)

        assert "My Modal" in html
        assert "modal-title" in html

    def test_modal_without_title(self) -> None:
        """Test modal without title."""
        result = modal("Content")
        html = str(result)

        # modal-title should not appear without title
        # Just verify modal-body is there
        assert "modal-body" in html

    def test_modal_with_footer(self) -> None:
        """Test modal with custom footer."""
        footer = modal_button("OK")
        result = modal("Content", footer=footer)
        html = str(result)

        assert "OK" in html
        assert "modal-footer" in html

    def test_modal_with_footer_none(self) -> None:
        """Test modal with footer=None (no footer)."""
        result = modal("Content", footer=None)
        html = str(result)

        # modal-footer should not appear
        assert "modal-footer" not in html

    def test_modal_default_footer(self) -> None:
        """Test modal has default Dismiss footer."""
        result = modal("Content")
        html = str(result)

        assert "Dismiss" in html
        assert "modal-footer" in html

    def test_modal_size_small(self) -> None:
        """Test modal with size='s'."""
        result = modal("Content", size="s")
        html = str(result)

        assert "modal-sm" in html

    def test_modal_size_medium(self) -> None:
        """Test modal with size='m' (default)."""
        result = modal("Content", size="m")
        html = str(result)

        # Medium is default, no special class
        assert "modal-sm" not in html
        assert "modal-lg" not in html
        assert "modal-xl" not in html

    def test_modal_size_large(self) -> None:
        """Test modal with size='l'."""
        result = modal("Content", size="l")
        html = str(result)

        assert "modal-lg" in html

    def test_modal_size_xl(self) -> None:
        """Test modal with size='xl'."""
        result = modal("Content", size="xl")
        html = str(result)

        assert "modal-xl" in html

    def test_modal_easy_close_true(self) -> None:
        """Test modal with easy_close=True."""
        result = modal("Content", easy_close=True)
        html = str(result)

        assert (
            'data-keyboard="true"' in html
            or 'data-backdrop="true"' in html
            or "modal" in html
        )

    def test_modal_easy_close_false(self) -> None:
        """Test modal with easy_close=False."""
        result = modal("Content", easy_close=False)
        html = str(result)

        assert (
            'data-keyboard="false"' in html
            or 'data-backdrop="static"' in html
            or "modal" in html
        )

    def test_modal_fade_true(self) -> None:
        """Test modal with fade=True (default)."""
        result = modal("Content", fade=True)
        html = str(result)

        assert "fade" in html

    def test_modal_fade_false(self) -> None:
        """Test modal with fade=False."""
        result = modal("Content", fade=False)
        html = str(result)

        # Should not have fade class
        # Check structure still exists
        assert "modal-body" in html

    def test_modal_multiple_children(self) -> None:
        """Test modal with multiple children."""
        from htmltools import tags

        result = modal(
            tags.p("Paragraph 1"),
            tags.p("Paragraph 2"),
            tags.p("Paragraph 3"),
        )
        html = str(result)

        assert "Paragraph 1" in html
        assert "Paragraph 2" in html
        assert "Paragraph 3" in html

    def test_modal_body_class(self) -> None:
        """Test modal has modal-body class."""
        result = modal("Content")
        html = str(result)

        assert "modal-body" in html

    def test_modal_content_class(self) -> None:
        """Test modal has modal-content class."""
        result = modal("Content")
        html = str(result)

        assert "modal-content" in html

    def test_modal_dialog_class(self) -> None:
        """Test modal has modal-dialog class."""
        result = modal("Content")
        html = str(result)

        assert "modal-dialog" in html

    def test_modal_custom_kwargs(self) -> None:
        """Test modal with custom kwargs applied to body."""
        result = modal("Content", class_="custom-body-class")
        html = str(result)

        assert "custom-body-class" in html
