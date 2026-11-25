"""Tests for `shiny.ui.input_text_area()`."""

from __future__ import annotations

from htmltools import Tag

from shiny import ui


def _textarea(x: Tag) -> Tag:
    textareas = [
        child
        for child in x.children
        if isinstance(child, Tag) and child.name == "textarea"
    ]
    assert len(textareas) == 1
    return textareas[0]


class TestInputTextAreaWidth:
    def test_width_is_applied_to_the_textarea(self):
        area = ui.input_text_area("x", "Label", width="600px")

        # The container carries the requested width and the textarea fills it.
        assert area.attrs.get("style") == "width:600px;"
        assert _textarea(area).attrs.get("style") == "width:100%;"

    def test_no_width_leaves_the_textarea_without_inline_width(self):
        area = ui.input_text_area("x", "Label", cols=20)

        textarea = _textarea(area)
        assert area.attrs.get("style") is None
        assert textarea.attrs.get("style") is None
        assert textarea.attrs.get("cols") == "20"

    def test_height_is_independent_of_width(self):
        area = ui.input_text_area("x", "Label", height="200px")

        assert _textarea(area).attrs.get("style") == "height:200px;"
