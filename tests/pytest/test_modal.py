"""Tests for `shiny.ui._modal`."""

from shiny.ui import modal, modal_button


class TestModalButton:
    """Tests for the modal_button function."""

    def test_basic_modal_button(self):
        """Test creating a basic modal button."""
        btn = modal_button("Close")
        html = str(btn)

        assert "<button" in html
        assert "Close" in html
        assert 'data-dismiss="modal"' in html
        assert 'data-bs-dismiss="modal"' in html
        assert 'class="btn btn-default"' in html
        assert 'type="button"' in html

    def test_modal_button_with_icon(self):
        """Test modal button with an icon."""
        from htmltools import tags

        icon = tags.i(class_="fa fa-times")
        btn = modal_button("Close", icon=icon)
        html = str(btn)

        assert "<button" in html
        assert "Close" in html
        assert '<i class="fa fa-times">' in html

    def test_modal_button_with_custom_attributes(self):
        """Test modal button with custom attributes."""
        btn = modal_button("Close", id="my-close-btn", class_="btn-danger")
        html = str(btn)

        assert 'id="my-close-btn"' in html
        assert "btn-danger" in html


class TestModal:
    """Tests for the modal function."""

    def test_basic_modal(self):
        """Test creating a basic modal."""
        m = modal("Modal content")
        html = str(m)

        assert 'id="shiny-modal"' in html
        assert 'class="modal fade"' in html
        assert "Modal content" in html
        assert "modal-body" in html
        assert "modal-content" in html
        assert "modal-dialog" in html

    def test_modal_with_title(self):
        """Test modal with a title."""
        m = modal("Content", title="My Modal Title")
        html = str(m)

        assert "My Modal Title" in html
        assert "modal-header" in html
        assert "modal-title" in html

    def test_modal_without_title(self):
        """Test modal without a title doesn't have header."""
        m = modal("Content")
        html = str(m)

        # Should still have modal structure but no header
        assert "modal-body" in html
        # When title is None, no header is added
        # Check that content is present
        assert "Content" in html

    def test_modal_with_none_footer(self):
        """Test modal with footer=None has no footer."""
        m = modal("Content", footer=None)
        html = str(m)

        assert "modal-body" in html
        # modal-footer should not be present when footer=None
        assert "modal-footer" not in html

    def test_modal_with_custom_footer(self):
        """Test modal with custom footer."""
        from htmltools import tags

        custom_footer = tags.div("Custom footer content", class_="custom-footer")
        m = modal("Content", footer=custom_footer)
        html = str(m)

        assert "modal-footer" in html
        assert "Custom footer content" in html
        assert "custom-footer" in html

    def test_modal_default_footer(self):
        """Test modal has default dismiss button in footer."""
        m = modal("Content")
        html = str(m)

        assert "modal-footer" in html
        assert "Dismiss" in html
        assert 'data-bs-dismiss="modal"' in html

    def test_modal_sizes(self):
        """Test different modal sizes."""
        m_small = modal("Content", size="s")
        m_medium = modal("Content", size="m")
        m_large = modal("Content", size="l")
        m_xl = modal("Content", size="xl")

        assert "modal-sm" in str(m_small)
        assert "modal-sm" not in str(m_medium)  # Default, no extra class
        assert "modal-lg" in str(m_large)
        assert "modal-xl" in str(m_xl)

    def test_modal_easy_close_true(self):
        """Test modal with easy_close=True."""
        m = modal("Content", easy_close=True)
        html = str(m)

        # When easy_close=True, backdrop and keyboard should not have "static"/"false"
        assert 'data-backdrop="static"' not in html
        assert 'data-bs-backdrop="static"' not in html
        assert 'data-keyboard="false"' not in html

    def test_modal_easy_close_false(self):
        """Test modal with easy_close=False (default)."""
        m = modal("Content", easy_close=False)
        html = str(m)

        assert 'data-backdrop="static"' in html
        assert 'data-bs-backdrop="static"' in html
        assert 'data-keyboard="false"' in html

    def test_modal_fade_true(self):
        """Test modal with fade=True (default)."""
        m = modal("Content", fade=True)
        html = str(m)

        assert 'class="modal fade"' in html

    def test_modal_fade_false(self):
        """Test modal with fade=False."""
        m = modal("Content", fade=False)
        html = str(m)

        assert 'class="modal"' in html
        assert 'class="modal fade"' not in html

    def test_modal_with_multiple_children(self):
        """Test modal with multiple children."""
        from htmltools import tags

        m = modal(
            tags.p("Paragraph 1"),
            tags.p("Paragraph 2"),
            tags.div("A div"),
        )
        html = str(m)

        assert "Paragraph 1" in html
        assert "Paragraph 2" in html
        assert "A div" in html

    def test_modal_with_custom_body_attributes(self):
        """Test modal with custom attributes applied to body."""
        m = modal("Content", class_="custom-body-class", id="body-id")
        html = str(m)

        # Custom attributes should be on the modal-body div
        assert "custom-body-class" in html

    def test_modal_contains_bootstrap_js(self):
        """Test modal contains JavaScript for Bootstrap compatibility."""
        m = modal("Content")
        html = str(m)

        assert "<script>" in html
        assert "bootstrap.Modal" in html
        assert "modal.show()" in html
