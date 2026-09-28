"""Tests for `shiny.ui.input_text_area()`."""

from __future__ import annotations

from shiny import ui


def _textarea_style(x: ui.Tag) -> str:
    textarea = x.get_html_string()
    start = textarea.index("<textarea")
    end = textarea.index(">", start)
    return textarea[start:end]


class TestInputTextAreaWidth:
    def test_width_is_applied_to_the_textarea(self):
        # Arrange / Act
        area = ui.input_text_area("x", "Label", width="600px")

        # Assert: the container carries the requested width and the textarea
        # fills it, so the field is as wide as the caller asked for.
        assert 'style="width:600px;"' in area.get_html_string()
        assert "width:100%" in _textarea_style(area)

    def test_no_width_leaves_the_textarea_unstyled(self):
        # Arrange / Act
        area = ui.input_text_area("x", "Label", cols=20)

        # Assert: without a CSS width rule, `cols` decides the width, which is
        # what the `cols` documentation promises.
        assert "width" not in _textarea_style(area)
        assert 'cols="20"' in _textarea_style(area)

    def test_height_is_independent_of_width(self):
        # Arrange / Act
        area = ui.input_text_area("x", "Label", height="200px")

        # Assert
        style = _textarea_style(area)
        assert "height:200px" in style
        assert "width" not in style
