"""Comprehensive tests for shiny.ui._modal module."""

import pytest  # noqa: F401
from htmltools import Tag


class TestModalButton:
    """Tests for modal_button function."""

    def test_modal_button_basic(self):
        """modal_button should create a button with correct attributes."""
        from shiny.ui import modal_button

        result = modal_button("Close")
        assert isinstance(result, Tag)
        assert result.name == "button"
        assert result.attrs.get("type") == "button"
        assert result.attrs.get("data-dismiss") == "modal"
        assert result.attrs.get("data-bs-dismiss") == "modal"

    def test_modal_button_with_label(self):
        """modal_button should render label correctly."""
        from shiny.ui import modal_button

        result = modal_button("My Label")
        # Check that label is in children
        assert "My Label" in str(result)

    def test_modal_button_with_icon(self):
        """modal_button should include icon."""
        from shiny.ui import modal_button

        result = modal_button("Close", icon="X")
        # Icon should be first child
        html_str = str(result)
        assert "X" in html_str

    def test_modal_button_with_kwargs(self):
        """modal_button should accept additional attributes."""
        from shiny.ui import modal_button

        result = modal_button("Close", id="my_btn", custom_attr="value")
        assert result.attrs.get("id") == "my_btn"
        # Underscores in kwargs are converted to hyphens in HTML
        assert result.attrs.get("custom-attr") == "value"

    def test_modal_button_has_default_class(self):
        """modal_button should have Bootstrap classes."""
        from shiny.ui import modal_button

        result = modal_button("Close")
        assert "btn" in result.attrs.get("class", "")
        assert "btn-default" in result.attrs.get("class", "")


class TestModal:
    """Tests for modal function."""

    def test_modal_basic(self):
        """modal should create a modal dialog."""
        from shiny.ui import modal

        result = modal("Content")
        assert isinstance(result, Tag)
        assert result.attrs.get("id") == "shiny-modal"
        assert "modal" in result.attrs.get("class", "")

    def test_modal_with_title(self):
        """modal should include title in header."""
        from shiny.ui import modal

        result = modal("Content", title="My Title")
        html_str = str(result)
        assert "My Title" in html_str
        assert "modal-title" in html_str

    def test_modal_without_title(self):
        """modal without title should not have header."""
        from shiny.ui import modal

        result = modal("Content", title=None)
        html_str = str(result)
        assert "modal-title" not in html_str

    def test_modal_default_footer(self):
        """modal should have default Dismiss button in footer."""
        from shiny.ui import modal

        result = modal("Content")
        html_str = str(result)
        assert "Dismiss" in html_str
        assert "modal-footer" in html_str

    def test_modal_custom_footer(self):
        """modal should accept custom footer."""
        from shiny.ui import modal

        result = modal("Content", footer="Custom Footer")
        html_str = str(result)
        assert "Custom Footer" in html_str

    def test_modal_no_footer(self):
        """modal with footer=None should have no footer."""
        from shiny.ui import modal

        result = modal("Content", footer=None)
        html_str = str(result)
        assert "modal-footer" not in html_str

    def test_modal_size_small(self):
        """modal with size='s' should have modal-sm class."""
        from shiny.ui import modal

        result = modal("Content", size="s")
        html_str = str(result)
        assert "modal-sm" in html_str

    def test_modal_size_medium(self):
        """modal with size='m' should have no size class."""
        from shiny.ui import modal

        result = modal("Content", size="m")
        html_str = str(result)
        assert "modal-sm" not in html_str
        assert "modal-lg" not in html_str
        assert "modal-xl" not in html_str

    def test_modal_size_large(self):
        """modal with size='l' should have modal-lg class."""
        from shiny.ui import modal

        result = modal("Content", size="l")
        html_str = str(result)
        assert "modal-lg" in html_str

    def test_modal_size_extra_large(self):
        """modal with size='xl' should have modal-xl class."""
        from shiny.ui import modal

        result = modal("Content", size="xl")
        html_str = str(result)
        assert "modal-xl" in html_str

    def test_modal_easy_close_false(self):
        """modal with easy_close=False should have backdrop static."""
        from shiny.ui import modal

        result = modal("Content", easy_close=False)
        assert result.attrs.get("data-backdrop") == "static"
        assert result.attrs.get("data-bs-backdrop") == "static"
        assert result.attrs.get("data-keyboard") == "false"
        assert result.attrs.get("data-bs-keyboard") == "false"

    def test_modal_easy_close_true(self):
        """modal with easy_close=True should not have backdrop static."""
        from shiny.ui import modal

        result = modal("Content", easy_close=True)
        assert result.attrs.get("data-backdrop") is None
        assert result.attrs.get("data-bs-backdrop") is None
        assert result.attrs.get("data-keyboard") is None
        assert result.attrs.get("data-bs-keyboard") is None

    def test_modal_fade_true(self):
        """modal with fade=True should have fade class."""
        from shiny.ui import modal

        result = modal("Content", fade=True)
        assert "fade" in result.attrs.get("class", "")

    def test_modal_fade_false(self):
        """modal with fade=False should not have fade class."""
        from shiny.ui import modal

        result = modal("Content", fade=False)
        assert "fade" not in result.attrs.get("class", "")

    def test_modal_with_multiple_children(self):
        """modal should accept multiple children."""
        from shiny.ui import modal

        result = modal("First", "Second", "Third")
        html_str = str(result)
        assert "First" in html_str
        assert "Second" in html_str
        assert "Third" in html_str

    def test_modal_has_javascript(self):
        """modal should include Bootstrap modal initialization script."""
        from shiny.ui import modal

        result = modal("Content")
        html_str = str(result)
        assert "bootstrap.Modal" in html_str or "modal()" in html_str

    def test_modal_with_kwargs(self):
        """modal should pass kwargs to body."""
        from shiny.ui import modal

        result = modal("Content", data_test="value")
        # kwargs should be applied to modal-body div
        html_str = str(result)
        assert "data-test" in html_str


class TestModalShow:
    """Tests for modal_show function."""

    def test_modal_show_requires_session(self):
        """modal_show should require an active session."""
        from shiny.ui import modal, modal_show

        m = modal("Test")
        # Without session context, should raise an error
        with pytest.raises(RuntimeError):
            modal_show(m, session=None)


class TestModalRemove:
    """Tests for modal_remove function."""

    def test_modal_remove_requires_session(self):
        """modal_remove should require an active session."""
        from shiny.ui import modal_remove

        # Without session context, should raise an error
        with pytest.raises(RuntimeError):
            modal_remove(session=None)


class TestModuleExports:
    """Tests for module exports."""

    def test_all_exports_exist(self):
        """All items in __all__ should be importable."""
        from shiny.ui import _modal

        for item in _modal.__all__:
            assert hasattr(_modal, item)

    def test_module_imports_correctly(self):
        """Module should import without errors."""
        import shiny.ui._modal as modal_module

        assert modal_module is not None
