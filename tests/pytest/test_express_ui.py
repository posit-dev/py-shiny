from __future__ import annotations

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
    the item in `_known_missing_express_ui`.
    These entries are in `_known_missing_express_ui` in shiny/express/ui/__init__.py
    """

    ui_all = set(ui.__all__)
    xui_all = set(xui.__all__)
    ui_known_missing = set(xui._known_missing_express_ui["shiny.ui"])
    xui_known_missing = set(xui._known_missing_express_ui["shiny.express.ui"])

    # Make sure that there's no overlap between shiny.express.ui.__all__ and
    # _known_missing_express_ui["shiny.ui"]; and same for other combinations. Note that the use of
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
    # explicitly listed in shiny.express.ui._known_missing_express_ui.
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

    @render.download_button
    def dl_btn():
        yield "data"

    assert (
        ui.TagList(dl_btn.tagify()).get_html_string()
        == ui.download_button("dl_btn", label="Download").get_html_string()
    )

    @render.download_link
    def dl_link():
        yield "data"

    assert (
        ui.TagList(dl_link.tagify()).get_html_string()
        == ui.download_link("dl_link", label="Download").get_html_string()
    )


def test_render_output_controls_complete():
    """
    Enforce the 1:1 mapping between output render decorators and output UI components.
    A new output renderer or output UI component that is not paired (and not explicitly
    allowlisted in `_known_missing_renderer`) fails this test.
    """
    import inspect

    from shiny.render._render import (
        _known_missing_renderer,
        _renderer_output_ui_pairs,
    )
    from shiny.render.renderer import Renderer

    # (1) Every mapped renderer's auto-placed UI matches its UI component's HTML.
    for renderer_cls, ui_fn in _renderer_output_ui_pairs.items():
        fn_name = renderer_cls.__name__

        @renderer_cls
        def out():
            yield "x"

        rendered = ui.TagList(out.tagify()).get_html_string()
        # Some UI components (e.g. download_button/download_link) have a required
        # `label` parameter with no default; auto_output_ui() supplies the renderer's
        # own default ("Download") for it, so mirror that here for a fair comparison.
        ui_fn_kwargs: dict[str, Any] = {}
        ui_fn_sig = inspect.signature(ui_fn)
        if (
            "label" in ui_fn_sig.parameters
            and ui_fn_sig.parameters["label"].default is inspect.Parameter.empty
        ):
            ui_fn_kwargs["label"] = "Download"
        expected = ui.TagList(ui_fn("out", **ui_fn_kwargs)).get_html_string()
        assert rendered == expected, f"{fn_name} auto_output_ui mismatch"

    # (2) Every Renderer subclass exported by shiny.render is mapped or allowlisted.
    mapped_renderers = {cls.__name__ for cls in _renderer_output_ui_pairs}
    allowed_renderers = set(_known_missing_renderer["shiny.render"])
    for name in render.__all__:
        obj = getattr(render, name)
        if inspect.isclass(obj) and issubclass(obj, Renderer):
            assert name in mapped_renderers or name in allowed_renderers, (
                f"render.{name} is a Renderer with no paired UI component; "
                f"add it to _renderer_output_ui_pairs or _known_missing_renderer"
            )

    # (3) Every output_*/download_* UI component is a mapping target or allowlisted.
    mapped_ui = {fn.__name__ for fn in _renderer_output_ui_pairs.values()}
    allowed_ui = set(_known_missing_renderer["shiny.ui"])
    for name in ui.__all__:
        if name.startswith("output_") or name.startswith("download_"):
            assert name in mapped_ui or name in allowed_ui, (
                f"ui.{name} is an output component with no paired renderer; "
                f"add it to _renderer_output_ui_pairs or _known_missing_renderer"
            )


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

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir, "temp.file")
        temp_file.write_text(card_app_express_text)
        res = run_express(temp_file).tagify()

    assert str(res) == str(card_app_core)
