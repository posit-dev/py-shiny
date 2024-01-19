import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

from shiny import render, ui
from shiny.express import output_args
from shiny.express import ui as xui
from shiny.express._run import run_express


def test_express_ui_is_complete():
    """
    Make sure shiny.express.ui covers everything that shiny.ui does, or explicitly lists
    the item in `_known_missing`.
    These entries are in `_known_missing` in shiny/express/ui/__init__.py
    """

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
        == ui.output_text("text1").get_html_string()
    )

    @output_args(placeholder=False)
    @render.code
    def code1():
        return "text"

    assert (
        ui.TagList(code1.tagify()).get_html_string()
        == ui.output_code("code1", placeholder=False).get_html_string()
    )

    @output_args(width=100)
    @render.code
    def code2():
        return "text"

    with pytest.raises(TypeError, match="width"):
        code2.tagify()


def test_hold():
    old_displayhook = sys.displayhook
    try:
        called = False

        def display_hook_spy(_: object) -> Any:
            nonlocal called
            called = True

        sys.displayhook = display_hook_spy

        with xui.hold():
            sys.displayhook("foo")

        assert not called

        sys.displayhook("baz")
        assert called

        called = False
        with xui.hold() as held:
            sys.displayhook("foo")
        assert not called
        sys.displayhook(held)
        assert called

    finally:
        sys.displayhook = old_displayhook


def test_recall_context_manager():
    # A Shiny Express app that uses a RecallContextManager (ui.card_header()) without
    # `with`. It is used within another RecallContextManager (ui.card()), but that one
    # is used with `with`. This test makes sure that the non-with RecallContextManager
    # will invoke the wrapped function and its result will be passed to the parent.

    card_app_express_text = """\
from shiny.express import ui

with ui.card():
    ui.card_header("Header")
    "Body"
"""

    # The same UI, written in the Shiny Core style.
    card_app_core = ui.page_fixed(
        ui.card(
            ui.card_header("Header"),
            "Body",
        )
    )

    with tempfile.NamedTemporaryFile(mode="w+t") as temp_file:
        temp_file.write(card_app_express_text)
        temp_file.flush()
        res = run_express(Path(temp_file.name)).tagify()

    assert str(res) == str(card_app_core)
