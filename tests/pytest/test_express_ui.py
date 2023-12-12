import sys
from typing import Any

import pytest

from shiny import render, ui
from shiny.express import output_args, suspend_display


def test_express_ui_is_complete():
    """
    Make sure shiny.express.ui covers everything that shiny.ui does, or explicitly lists
    the item in _known_missing.
    """

    from shiny import ui
    from shiny.express import ui as xui

    ui_all = set(ui.__all__)
    xui_all = set(xui.__all__)
    ui_known_missing = set(xui._known_missing["shiny.ui"])
    xui_known_missing = set(xui._known_missing["shiny.express.ui"])

    # Make sure that in shiny.express.ui, there's no overlap between __all__ and
    # _known_missing.
    assert xui_all.isdisjoint(ui_known_missing)

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

    @output_args(placeholder=True)
    @render.text
    def text3():
        return "text"

    assert (
        ui.TagList(text3.tagify()).get_html_string()
        == ui.output_text_verbatim("text3", placeholder=True).get_html_string()
    )

    @output_args(width=100)
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
