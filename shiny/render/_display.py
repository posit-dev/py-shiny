from __future__ import annotations

import inspect
import sys
from typing import Any, Callable, Optional, Union, overload

from htmltools import TagAttrValue, TagFunction, TagList, wrap_displayhook_handler

from .. import ui as _ui
from ..session._utils import RenderedDeps
from .transformer import (
    OutputRendererSync,
    TransformerMetadata,
    TransformerParams,
    ValueFn,
    ValueFnSync,
)


async def DisplayTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[None],
    *,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    fill: bool = False,
    fillable: bool = False,
    **kwargs: TagAttrValue,
) -> RenderedDeps | None:
    results: list[object] = []
    orig_displayhook = sys.displayhook
    sys.displayhook = wrap_displayhook_handler(results.append)
    try:
        x = _fn()
        if inspect.iscoroutine(x):
            raise TypeError(
                "@render.display does not support async functions. Use @render.ui instead."
            )
    finally:
        sys.displayhook = orig_displayhook
    if len(results) == 0:
        return None
    return _meta.session._process_ui(
        TagList(*results)  # pyright: ignore[reportGeneralTypeIssues]
    )


DisplayRenderer = OutputRendererSync[Union[RenderedDeps, None]]


@overload
def display(
    *,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    fill: bool = False,
    fillable: bool = False,
    **kwargs: Any,
) -> Callable[[ValueFnSync[None]], DisplayRenderer]:
    ...


@overload
def display(
    _fn: ValueFnSync[None],
) -> DisplayRenderer:
    ...


def display(
    _fn: ValueFnSync[None] | None = None,
    *,
    inline: bool = False,
    container: Optional[TagFunction] = None,
    fill: bool = False,
    fillable: bool = False,
    **kwargs: Any,
) -> DisplayRenderer | Callable[[ValueFnSync[None]], DisplayRenderer]:
    """
    Reactively render UI content, emitting each top-level expression of the function
    body, in the same way as a Shiny Express top-level or Jupyter notebook cell.

    Parameters
    ----------
    inline
        If ``True``, the rendered content will be displayed inline with the surrounding
        text. If ``False``, the rendered content will be displayed on its own line. If
        the ``container`` argument is not ``None``, this argument is ignored.
    container
        A function that returns a container for the rendered content. If ``None``, a
        default container will be chosen according to the ``inline`` argument.
    fill
        Whether or not to allow the UI output to grow/shrink to fit a fillable container
        with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    fillable
        Whether or not the UI output area should be considered a fillable (i.e.,
        flexbox) container.
    **kwargs
        Attributes to be applied to the output container.


    Returns
    -------
    :
        A decorator for a function whose top-level expressions will be displayed as UI.
    """

    def impl(fn: ValueFnSync[None]) -> OutputRendererSync[RenderedDeps | None]:
        from shiny.express.display_decorator._display_body import (
            display_body_unwrap_inplace,
        )

        fn = display_body_unwrap_inplace()(fn)
        return OutputRendererSync(
            fn,
            DisplayTransformer,
            TransformerParams(
                inline=inline,
                container=container,
                fill=fill,
                fillable=fillable,
                **kwargs,
            ),
            default_ui=_ui.output_ui,
            default_ui_passthrough_args=(
                "inline",
                "container",
                "fill",
                "fillable",
                *[k for k in kwargs.keys()],
            ),
        )

    if _fn is not None:
        return impl(_fn)
    else:
        return impl
