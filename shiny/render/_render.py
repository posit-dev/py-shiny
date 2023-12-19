from __future__ import annotations

__all__ = (
    "text",
    "plot",
    "image",
    "table",
    "ui",
)

import base64
import os
import sys
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Optional,
    Protocol,
    Union,
    cast,
    overload,
    runtime_checkable,
)

from htmltools import TagChild

if TYPE_CHECKING:
    from ..session._utils import RenderedDeps
    import pandas as pd

from .. import _utils
from .. import ui as _ui
from .._namespaces import ResolvedId
from ..types import MISSING, MISSING_TYPE, ImgData
from ._try_render_plot import (
    PlotSizeInfo,
    try_render_matplotlib,
    try_render_pil,
    try_render_plotnine,
)
from .transformer import (
    TransformerMetadata,
    ValueFn,
    is_async_callable,
    output_transformer,
    resolve_value_fn,
)

# ======================================================================================
# RenderText
# ======================================================================================


@output_transformer(default_ui=_ui.output_text_verbatim)
async def TextTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[str | None],
) -> str | None:
    value = await resolve_value_fn(_fn)
    if value is None:
        return None
    return str(value)


@overload
def text() -> TextTransformer.OutputRendererDecorator:
    ...


@overload
def text(_fn: TextTransformer.ValueFn) -> TextTransformer.OutputRenderer:
    ...


def text(
    _fn: TextTransformer.ValueFn | None = None,
) -> TextTransformer.OutputRenderer | TextTransformer.OutputRendererDecorator:
    """
    Reactively render text.

    Returns
    -------
    :
        A decorator for a function that returns a string.

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_text` container (see :func:`~shiny.ui.output_text` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_text
    """
    return TextTransformer(_fn)


# ======================================================================================
# RenderPlot
# ======================================================================================


# It would be nice to specify the return type of RenderPlotFunc to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.
@output_transformer(
    default_ui=_ui.output_plot, default_ui_passthrough_args=("width", "height")
)
async def PlotTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[object],
    *,
    alt: Optional[str] = None,
    width: float | None | MISSING_TYPE = MISSING,
    height: float | None | MISSING_TYPE = MISSING,
    **kwargs: object,
) -> ImgData | None:
    is_userfn_async = is_async_callable(_fn)
    name = _meta.name
    session = _meta.session

    inputs = session.root_scope().input

    # We don't have enough information at this point to decide what size the plot should
    # be. This is because the user's plotting code itself may express an opinion about
    # the plot size. We'll take the information we will need and stash it in
    # PlotSizeInfo, which then gets passed into the various plotting strategies.

    # Reactively read some information about the plot.
    pixelratio: float = typing.cast(
        float, inputs[ResolvedId(".clientdata_pixelratio")]()
    )

    # Do NOT call this unless you actually are going to respect the container dimension
    # you're asking for. It takes a reactive dependency. If the client hasn't reported
    # the requested dimension, you'll get a SilentException.
    def container_size(dimension: Literal["width", "height"]) -> float:
        result = inputs[ResolvedId(f".clientdata_output_{name}_{dimension}")]()
        return typing.cast(float, result)

    non_missing_size = (
        cast(Union[float, None], width) if width is not MISSING else None,
        cast(Union[float, None], height) if height is not MISSING else None,
    )
    plot_size_info = PlotSizeInfo(
        container_size_px_fn=(
            lambda: container_size("width"),
            lambda: container_size("height"),
        ),
        user_specified_size_px=non_missing_size,
        pixelratio=pixelratio,
    )

    # Call the user function to get the plot object.
    x = await resolve_value_fn(_fn)

    # Note that x might be None; it could be a matplotlib.pyplot

    # Try each type of renderer in turn. The reason we do it this way is to avoid
    # importing modules that aren't already loaded. That could slow things down, or
    # worse, cause an error if the module isn't installed.
    #
    # Each try_render function should indicate whether it was able to make sense of
    # the x value (or, in the case of matplotlib, possibly it decided to use the
    # global pyplot figure) by returning a tuple that starts with True. The second
    # tuple element may be None in this case, which means the try_render function
    # explicitly wants the plot to be blanked.
    #
    # If a try_render function returns a tuple that starts with False, then the next
    # try_render function should be tried. If none succeed, an error is raised.
    ok: bool
    result: ImgData | None

    if "plotnine" in sys.modules:
        ok, result = try_render_plotnine(
            x,
            plot_size_info=plot_size_info,
            alt=alt,
            **kwargs,
        )
        if ok:
            return result

    if "matplotlib" in sys.modules:
        ok, result = try_render_matplotlib(
            x,
            plot_size_info=plot_size_info,
            allow_global=not is_userfn_async,
            alt=alt,
            **kwargs,
        )
        if ok:
            return result

    if "PIL" in sys.modules:
        ok, result = try_render_pil(
            x,
            plot_size_info=plot_size_info,
            alt=alt,
            **kwargs,
        )
        if ok:
            return result

    # This check must happen last because
    # matplotlib might be able to plot even if x is `None`
    if x is None:
        return None

    raise Exception(
        f"@render.plot doesn't know to render objects of type '{str(type(x))}'. "
        + "Consider either requesting support for this type of plot object, and/or "
        + " explictly saving the object to a (png) file and using @render.image."
    )


@overload
def plot(
    *,
    alt: Optional[str] = None,
    width: float | None | MISSING_TYPE = MISSING,
    height: float | None | MISSING_TYPE = MISSING,
    **kwargs: Any,
) -> PlotTransformer.OutputRendererDecorator:
    ...


@overload
def plot(_fn: PlotTransformer.ValueFn) -> PlotTransformer.OutputRenderer:
    ...


def plot(
    _fn: PlotTransformer.ValueFn | None = None,
    *,
    alt: Optional[str] = None,
    width: float | None | MISSING_TYPE = MISSING,
    height: float | None | MISSING_TYPE = MISSING,
    **kwargs: Any,
) -> PlotTransformer.OutputRenderer | PlotTransformer.OutputRendererDecorator:
    """
    Reactively render a plot object as an HTML image.

    Parameters
    ----------
    alt
        Alternative text for the image if it cannot be displayed or viewed (i.e., the
        user uses a screen reader).
    width
        Width of the plot in pixels. If ``None`` or ``MISSING``, the width will be
        determined by the size of the corresponding :func:`~shiny.ui.output_plot`. (You
        should not need to use this argument in most Shiny apps--set the desired width
        on :func:`~shiny.ui.output_plot` instead.)
    height
        Height of the plot in pixels. If ``None`` or ``MISSING``, the height will be
        determined by the size of the corresponding :func:`~shiny.ui.output_plot`. (You
        should not need to use this argument in most Shiny apps--set the desired height
        on :func:`~shiny.ui.output_plot` instead.)
    **kwargs
        Additional keyword arguments passed to the relevant method for saving the image
        (e.g., for matplotlib, arguments to ``savefig()``; for PIL and plotnine,
        arguments to ``save()``).

    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A :class:`matplotlib.figure.Figure` instance.
        2. An :class:`matplotlib.artist.Artist` instance.
        3. A list/tuple of Figure/Artist instances.
        4. An object with a 'figure' attribute pointing to a
           :class:`matplotlib.figure.Figure` instance.
        5. A :class:`PIL.Image.Image` instance.

    It's also possible to use the ``matplotlib.pyplot`` interface; in that case, your
    function should just call pyplot functions and not return anything. (Note that if
    the decorated function is async, then it's not safe to use pyplot. Shiny will detect
    this case and throw an error asking you to use matplotlib's object-oriented
    interface instead.)

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_plot` container (see :func:`~shiny.ui.output_plot` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_plot ~shiny.render.image
    """
    return PlotTransformer(
        _fn, PlotTransformer.params(alt=alt, width=width, height=height, **kwargs)
    )


# ======================================================================================
# RenderImage
# ======================================================================================
@output_transformer(default_ui=_ui.output_image)
async def ImageTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[ImgData | None],
    *,
    delete_file: bool = False,
) -> ImgData | None:
    res = await resolve_value_fn(_fn)
    if res is None:
        return None

    src: str = res.get("src")
    try:
        with open(src, "rb") as f:
            data = base64.b64encode(f.read())
            data_str = data.decode("utf-8")
        content_type = _utils.guess_mime_type(src)
        res["src"] = f"data:{content_type};base64,{data_str}"
        return res
    finally:
        if delete_file:
            os.remove(src)


@overload
def image(
    *,
    delete_file: bool = False,
) -> ImageTransformer.OutputRendererDecorator:
    ...


@overload
def image(_fn: ImageTransformer.ValueFn) -> ImageTransformer.OutputRenderer:
    ...


def image(
    _fn: ImageTransformer.ValueFn | None = None,
    *,
    delete_file: bool = False,
) -> ImageTransformer.OutputRendererDecorator | ImageTransformer.OutputRenderer:
    """
    Reactively render a image file as an HTML image.

    Parameters
    ----------
    delete_file
        If ``True``, the image file will be deleted after rendering.

    Returns
    -------
    :
        A decorator for a function that returns an :func:`~shiny.types.ImgData` object.

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_image` container (see :func:`~shiny.ui.output_image`
    for example usage).

    See Also
    --------
    ~shiny.ui.output_image
    ~shiny.types.ImgData
    ~shiny.render.plot
    """
    return ImageTransformer(_fn, ImageTransformer.params(delete_file=delete_file))


# ======================================================================================
# RenderTable
# ======================================================================================


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> "pd.DataFrame":
        ...


TableResult = Union["pd.DataFrame", PandasCompatible, None]


@output_transformer(default_ui=_ui.output_table)
async def TableTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[TableResult | None],
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: object,
) -> RenderedDeps | None:
    x = await resolve_value_fn(_fn)

    if x is None:
        return None

    import pandas
    import pandas.io.formats.style

    html: str
    if isinstance(x, pandas.io.formats.style.Styler):
        html = cast(  # pyright: ignore[reportUnnecessaryCast]
            str,
            x.to_html(**kwargs),  # pyright: ignore
        )
    else:
        if not isinstance(x, pandas.DataFrame):
            if not isinstance(x, PandasCompatible):
                raise TypeError(
                    "@render.table doesn't know how to render objects of type "
                    f"'{str(type(x))}'. Return either a pandas.DataFrame, or an object "
                    "that has a .to_pandas() method."
                )
            x = x.to_pandas()

        html = cast(  # pyright: ignore[reportUnnecessaryCast]
            str,
            x.to_html(  # pyright: ignore
                index=index,
                classes=classes,
                border=border,
                **kwargs,  # pyright: ignore[reportGeneralTypeIssues]
            ),
        )
    return {"deps": [], "html": html}


@overload
def table(
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: Any,
) -> TableTransformer.OutputRendererDecorator:
    ...


@overload
def table(_fn: TableTransformer.ValueFn) -> TableTransformer.OutputRenderer:
    ...


def table(
    _fn: TableTransformer.ValueFn | None = None,
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: object,
) -> TableTransformer.OutputRenderer | TableTransformer.OutputRendererDecorator:
    """
    Reactively render a pandas ``DataFrame`` object (or similar) as a basic HTML
    table.

    Consider using :func:`~shiny.render.data_frame` instead of this renderer, as
    it provides high performance virtual scrolling, built-in filtering and sorting,
    and a better default appearance. This renderer may still be helpful if you
    use pandas styling features that are not currently supported by
    :func:`~shiny.render.data_frame`.

    Parameters
    ----------
    index
        Whether to print index (row) labels. (Ignored for pandas :class:`Styler`
        objects; call ``style.hide(axis="index")`` from user code instead.)
    classes
        CSS classes (space separated) to apply to the resulting table. By default, we
        use `table shiny-table w-auto` which is designed to look reasonable with
        Bootstrap 5. (Ignored for pandas :class:`Styler` objects; call
        ``style.set_table_attributes('class="dataframe table shiny-table w-auto"')``
        from user code instead.)
    **kwargs
        Additional keyword arguments passed to ``pandas.DataFrame.to_html()`` or
        ``pandas.io.formats.style.Styler.to_html()``.

    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A pandas :class:`DataFrame` object.
        2. A pandas :class:`Styler` object.
        3. Any object that has a `.to_pandas()` method (e.g., a Polars data frame or
           Arrow table).

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_table` container (see :func:`~shiny.ui.output_table`
    for example usage).

    See Also
    --------
    ~shiny.ui.output_table for the corresponding UI component to this render function.
    """
    return TableTransformer(
        _fn,
        TableTransformer.params(
            index=index,
            classes=classes,
            border=border,
            **kwargs,
        ),
    )


# ======================================================================================
# RenderUI
# ======================================================================================
@output_transformer(default_ui=_ui.output_ui)
async def UiTransformer(
    _meta: TransformerMetadata,
    _fn: ValueFn[TagChild],
) -> RenderedDeps | None:
    ui = await resolve_value_fn(_fn)
    if ui is None:
        return None

    return _meta.session._process_ui(ui)


@overload
def ui() -> UiTransformer.OutputRendererDecorator:
    ...


@overload
def ui(_fn: UiTransformer.ValueFn) -> UiTransformer.OutputRenderer:
    ...


def ui(
    _fn: UiTransformer.ValueFn | None = None,
) -> UiTransformer.OutputRenderer | UiTransformer.OutputRendererDecorator:
    """
    Reactively render HTML content.

    Returns
    -------
    :
        A decorator for a function that returns an object of type
        :class:`~shiny.ui.TagChild`.

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_ui` container (see :func:`~shiny.ui.output_ui` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_ui
    """
    return UiTransformer(_fn)
