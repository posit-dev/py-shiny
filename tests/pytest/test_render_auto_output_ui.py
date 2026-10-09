from __future__ import annotations

import inspect
import types
import typing
from typing import Any, Callable

import htmltools
import htmltools._core
import pytest

from shiny import render, ui
from shiny.express import output_args
from shiny.render.renderer import Renderer
from shiny.types import MISSING_TYPE

# Resolve htmltools' forward references (e.g. `Tagifiable`, `HTML`)
_localns = {**vars(htmltools._core), **vars(htmltools)}


def _type_set(annotation: Any) -> set[Any]:
    # `X | MISSING_TYPE` in `auto_output_ui()` means "not given"; compare only `X`
    if typing.get_origin(annotation) in (typing.Union, types.UnionType):
        return set(typing.get_args(annotation)) - {MISSING_TYPE}
    return {annotation}


def _params(fn: Callable[..., object]) -> dict[str, set[Any]]:
    hints = typing.get_type_hints(fn, localns=_localns)
    return {
        # `**kwargs` keeps its name-independent key so both sides line up
        ("**" if p.kind is p.VAR_KEYWORD else name): _type_set(hints[name])
        for name, p in inspect.signature(fn).parameters.items()
        if name not in ("self", "id")
    }


@pytest.mark.parametrize(
    "renderer, ui_fn",
    [
        (render.text, ui.output_text),
        (render.code, ui.output_code),
        (render.plot, ui.output_plot),
        (render.image, ui.output_image),
        (render.table, ui.output_table),
        (render.ui, ui.output_ui),
        (render.express, ui.output_ui),
        (render.data_frame, ui.output_data_frame),
        # TODO: Remove the xfail once #2533 adds `icon` and `**kwargs`; `label` still
        # needs to be added to `auto_output_ui()` afterward
        pytest.param(
            render.download_button,
            ui.download_button,
            marks=pytest.mark.xfail(reason="#2533", strict=True),
        ),
        pytest.param(
            render.download_link,
            ui.download_link,
            marks=pytest.mark.xfail(reason="#2533", strict=True),
        ),
    ],
)
def test_auto_output_ui_matches_ui_fn(
    renderer: type[Renderer[Any]], ui_fn: Callable[..., object]
):
    # Every `@output_args()` value goes through `auto_output_ui()`, so it should accept
    # exactly the arguments (and types) of the UI function it calls
    params = _params(renderer.auto_output_ui)
    # An untyped catch-all hides which arguments are accepted
    assert params.get("**") != {object}, "Use explicit args, not `**kwargs: object`"
    assert params == _params(ui_fn)


def test_render_ui_takes_output_args():
    @output_args(fill=True, class_="foo")
    @render.ui
    def out():
        return "hi"

    expected = ui.output_ui("out", fill=True, class_="foo")
    assert str(out.tagify()) == str(expected)
