import sys
from typing import Any

import pytest

from shiny import render, ui
from shiny.express import suspend_display, ui_kwargs


def test_express_ui_is_complete():
    """
    Make sure shiny.express.ui covers everything that shiny.ui does, or explicitly lists
    the item in `_known_missing`.
    These entries are in `_known_missing` in shiny/express/ui/__init__.py
    """

    from shiny import ui
    from shiny.express import ui as xui

    ui_all = set(ui.__all__)
    xui_all = set(xui.__all__)
    ui_known_missing = set(xui._known_missing["shiny.ui"])
    xui_known_missing = set(xui._known_missing["shiny.express.ui"])

    # Make sure that there's no overlap between shiny.express.ui.__all__ and
    # _known_missing["shiny.ui"]; and same for other combinations. Note that the use of
    # `.intersection() == set()` instead of `disjoint()` is intentional, because if the
    # test fails, the first form provides an error message that shows the difference,
    # while the second form does note.
    assert xui_all.intersection(ui_known_missing) == set()
    assert ui_all.intersection(xui_known_missing) == set()

    # Similar to above, use .difference() instead of .issubset() to get better error
    # messages.
    assert xui_known_missing.difference(xui_all) == set()
    assert ui_known_missing.difference(ui_all) == set()

    # Make sure that everything from shiny.ui is either exported by shiny.express.ui, or
    # explicitly listed in shiny.express.ui._known_missing.
    assert ui_all.union(xui_known_missing) == xui_all.union(ui_known_missing)


def test_render_output_controls():
    @render.text
    def text1():
        return "text"

    assert (
        ui.TagList(text1.tagify()).get_html_string()
        == ui.output_text_verbatim("text1").get_html_string()
    )

    @suspend_display
    @render.text
    def text2():
        return "text"

    assert ui.TagList(text2.tagify()).get_html_string() == ""

    @ui_kwargs(placeholder=True)
    @render.text
    def text3():
        return "text"

    assert (
        ui.TagList(text3.tagify()).get_html_string()
        == ui.output_text_verbatim("text3", placeholder=True).get_html_string()
    )

    @ui_kwargs(width=100)
    @render.text
    def text4():
        return "text"

    with pytest.raises(TypeError, match="width"):
        text4.tagify()


def test_suspend_display():
    old_displayhook = sys.displayhook
    try:
        called = False

        def display_hook_spy(_: object) -> Any:
            nonlocal called
            called = True

        sys.displayhook = display_hook_spy

        with suspend_display():
            sys.displayhook("foo")
        suspend_display(lambda: sys.displayhook("bar"))()

        @suspend_display
        def whatever(x: Any):
            sys.displayhook(x)

        whatever(100)

        assert not called

        sys.displayhook("baz")
        assert called

    finally:
        sys.displayhook = old_displayhook
