from __future__ import annotations

import base64
import os
import sys
import typing
from typing import (
    TYPE_CHECKING,
    Literal,
    Optional,
    Protocol,
    Union,
    cast,
    runtime_checkable,
)

from htmltools import Tag, TagAttrValue, TagChild

from shiny.render.renderer import JSONifiable

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
from .renderer import Renderer, ValueFn

__all__ = (
    "text",
    "plot",
    "image",
    "table",
    "ui",
)
# ======================================================================================
# RenderText
# ======================================================================================


class text(Renderer[str]):
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

    def default_ui(self, id: str, placeholder: bool | MISSING_TYPE = MISSING) -> Tag:
        kwargs: dict[str, bool] = {}
        if not isinstance(placeholder, MISSING_TYPE):
            kwargs["placeholder"] = placeholder
        return _ui.output_text_verbatim(id, **kwargs)

    def __init__(self, fn: Optional[ValueFn[str]] = None, power: int = 1) -> None:
        super().__init__(fn)
        self.power: int = power

    async def transform(self, value: str) -> JSONifiable:
        return str(value)


# ======================================================================================
# RenderPlot
# ======================================================================================


# It would be nice to specify the return type of ValueFn to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.


class plot(Renderer[object]):
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

    def default_ui(
        self,
        id: str,
        *,
        width: str | float | int | MISSING_TYPE = MISSING,
        height: str | float | int | MISSING_TYPE = MISSING,
        **kwargs: object,
    ) -> Tag:
        def set_kwarg_value(
            key: str,
            ui_val: str | float | int | MISSING_TYPE,
            self_val: float | None | MISSING_TYPE,
        ):
            if not isinstance(ui_val, MISSING_TYPE):
                kwargs[key] = ui_val
                return
            if not (isinstance(self_val, MISSING_TYPE) or self_val is None):
                kwargs[key] = self_val
                return
            # Do nothing as we don't want to override the default value (that could change in the future)
            return

        # Only set the arg if it is available. (Prevents duplicating default values)
        set_kwarg_value("width", width, self.width)
        set_kwarg_value("height", height, self.height)
        return _ui.output_plot(
            id,
            # (possibly) contains `width` and `height` keys!
            **kwargs,  # pyright: ignore[reportGeneralTypeIssues]
        )

    def __init__(
        self,
        fn: Optional[ValueFn[object]] = None,
        *,
        alt: Optional[str] = None,
        width: float | None | MISSING_TYPE = MISSING,
        height: float | None | MISSING_TYPE = MISSING,
        **kwargs: object,
    ) -> None:
        super().__init__(fn)
        self.alt = alt
        self.width = width
        self.height = height
        self.kwargs = kwargs

    async def render(self) -> dict[str, JSONifiable] | JSONifiable | None:
        is_userfn_async = self.value_fn.is_async
        name = self.name
        session = self.session
        width = self.width
        height = self.height
        alt = self.alt
        kwargs = self.kwargs

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
        x = await self.value_fn()

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

        def cast_result(result: ImgData | None) -> dict[str, JSONifiable] | None:
            if result is None:
                return None
            img_dict = dict(result)
            img_jsonifiable = cast(dict[str, JSONifiable], img_dict)
            return img_jsonifiable

        if "plotnine" in sys.modules:
            ok, result = try_render_plotnine(
                x,
                plot_size_info=plot_size_info,
                alt=alt,
                **kwargs,
            )
            if ok:
                return cast_result(result)

        if "matplotlib" in sys.modules:
            ok, result = try_render_matplotlib(
                x,
                plot_size_info=plot_size_info,
                allow_global=not is_userfn_async,
                alt=alt,
                **kwargs,
            )
            if ok:
                return cast_result(result)

        if "PIL" in sys.modules:
            ok, result = try_render_pil(
                x,
                plot_size_info=plot_size_info,
                alt=alt,
                **kwargs,
            )
            if ok:
                return cast_result(result)

        # This check must happen last because
        # matplotlib might be able to plot even if x is `None`
        if x is None:
            return None

        raise Exception(
            f"@render.plot doesn't know to render objects of type '{str(type(x))}'. "
            + "Consider either requesting support for this type of plot object, and/or "
            + " explictly saving the object to a (png) file and using @render.image."
        )


# ======================================================================================
# RenderImage
# ======================================================================================
class image(Renderer[ImgData]):
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

    def default_ui(self, id: str, **kwargs: object):
        return _ui.output_image(
            id,
            **kwargs,  # pyright: ignore[reportGeneralTypeIssues]
        )

    def __init__(
        self,
        fn: Optional[ValueFn[ImgData]] = None,
        *,
        delete_file: bool = False,
    ) -> None:
        super().__init__(fn)
        self.delete_file: bool = delete_file

    async def transform(self, value: ImgData) -> dict[str, JSONifiable] | None:
        src: str = value.get("src")
        try:
            with open(src, "rb") as f:
                data = base64.b64encode(f.read())
                data_str = data.decode("utf-8")
            content_type = _utils.guess_mime_type(src)
            value["src"] = f"data:{content_type};base64,{data_str}"
            value_dict = dict(value)
            value_jsonifiable = cast(dict[str, JSONifiable], value_dict)
            return value_jsonifiable
        finally:
            if self.delete_file:
                os.remove(src)


# ======================================================================================
# RenderTable
# ======================================================================================


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> "pd.DataFrame":
        ...


TableResult = Union["pd.DataFrame", PandasCompatible, None]


class table(Renderer[TableResult]):
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

    def default_ui(self, id: str, **kwargs: TagAttrValue) -> Tag:
        return _ui.output_table(id, **kwargs)

    def __init__(
        self,
        fn: Optional[ValueFn[TableResult]] = None,
        *,
        index: bool = False,
        classes: str = "table shiny-table w-auto",
        border: int = 0,
        **kwargs: object,
    ) -> None:
        super().__init__(fn)
        self.index: bool = index
        self.classes: str = classes
        self.border: int = border
        self.kwargs: dict[str, object] = kwargs

    async def transform(self, value: TableResult) -> dict[str, JSONifiable]:
        import pandas
        import pandas.io.formats.style

        html: str
        if isinstance(value, pandas.io.formats.style.Styler):
            html = cast(  # pyright: ignore[reportUnnecessaryCast]
                str,
                value.to_html(**self.kwargs),  # pyright: ignore
            )
        else:
            if not isinstance(value, pandas.DataFrame):
                if not isinstance(value, PandasCompatible):
                    raise TypeError(
                        "@render.table doesn't know how to render objects of type "
                        f"'{str(type(value))}'. Return either a pandas.DataFrame, or an object "
                        "that has a .to_pandas() method."
                    )
                value = value.to_pandas()

            html = cast(  # pyright: ignore[reportUnnecessaryCast]
                str,
                value.to_html(  # pyright: ignore
                    index=self.index,
                    classes=self.classes,
                    border=self.border,
                    **self.kwargs,  # pyright: ignore[reportGeneralTypeIssues]
                ),
            )
        # Use typing to make sure the return shape matches
        ret: RenderedDeps = {"deps": [], "html": html}
        ret_dict = dict(ret)
        ret_jsonifiable = cast(dict[str, JSONifiable], ret_dict)
        return ret_jsonifiable


# ======================================================================================
# RenderUI
# ======================================================================================
class ui(Renderer[TagChild]):
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

    def default_ui(self, id: str) -> Tag:
        return _ui.output_ui(id)

    async def transform(self, value: TagChild) -> JSONifiable:
        res = self.session._process_ui(value)
        res_dict = dict(res)
        res_jsonifiable = cast(JSONifiable, res_dict)
        return res_jsonifiable
