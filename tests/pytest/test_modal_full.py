"""Tests for shiny/ui/_modal.py module."""

from shiny.ui._modal import modal, modal_button


class TestModal:
    """Tests for modal function."""

    def test_modal_is_callable(self):
        """Test modal is callable."""
        assert callable(modal)

    def test_modal_returns_tag(self):
        """Test modal returns a Tag."""
        from htmltools import Tag

        result = modal("Modal content")
        assert isinstance(result, Tag)

    def test_modal_with_title(self):
        """Test modal with title parameter."""
        from htmltools import Tag

        result = modal("Modal content", title="My Modal")
        assert isinstance(result, Tag)

    def test_modal_with_footer(self):
        """Test modal with footer parameter."""
        from htmltools import Tag

        result = modal("Modal content", footer=modal_button("Close"))
        assert isinstance(result, Tag)


class TestModalButton:
    """Tests for modal_button function."""

    def test_modal_button_is_callable(self):
        """Test modal_button is callable."""
        assert callable(modal_button)

    def test_modal_button_returns_tag(self):
        """Test modal_button returns a Tag."""
        from htmltools import Tag

        result = modal_button("Close")
        assert isinstance(result, Tag)


class TestModalExported:
    """Tests for modal functions export."""

    def test_modal_in_ui(self):
        """Test modal is in ui module."""
        from shiny import ui

        assert hasattr(ui, "modal")

    def test_modal_button_in_ui(self):
        """Test modal_button is in ui module."""
        from shiny import ui

        assert hasattr(ui, "modal_button")

    def test_modal_show_in_ui(self):
        """Test modal_show is in ui module."""
        from shiny import ui

        assert hasattr(ui, "modal_show")

    def test_modal_remove_in_ui(self):
        """Test modal_remove is in ui module."""
        from shiny import ui

        assert hasattr(ui, "modal_remove")
