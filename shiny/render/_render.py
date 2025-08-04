from __future__ import annotations

import base64
import os
import sys
import typing
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Union, cast

from htmltools import Tag, TagAttrValue, TagChild

from ._data_frame_utils._tbl_data import as_data_frame
from ._data_frame_utils._types import IntoDataFrame

if TYPE_CHECKING:

    from ..session._utils import RenderedDeps

from .. import _utils
from .. import ui as _ui
from .._docstring import add_example, no_example
from .._typing_extensions import Self
from ..module import ResolvedId
from ..session import get_current_session, require_active_session
from ..session._session import DownloadHandler, DownloadInfo
from ..types import MISSING, MISSING_TYPE, ImgData
from ._try_render_plot import (
    PlotSizeInfo,
    try_render_matplotlib,
    try_render_pil,
    try_render_plotnine,
)
from .renderer import Jsonifiable, Renderer, ValueFn
from .renderer._utils import (
    imgdata_to_jsonifiable,
    rendered_deps_to_jsonifiable,
    set_kwargs_value,
)

__all__ = (
    "text",
    "code",
    "plot",
    "image",
    "table",
    "ui",
    "download",
)
# ======================================================================================
# RenderText
# ======================================================================================


@add_example(ex_dir="../api-examples/output_text")
@no_example("express")
class text(Renderer[str]):
    """
    Reactively render text.

    When used in Shiny Express applications, this defaults to displaying the text as
    normal text on the web page. When used in Shiny Core applications, this should be
    paired with :func:`~shiny.ui.output_text` in the UI.


    Parameters
    ----------
    inline
        (Express only). If ``True``, the result is displayed inline. (This argument is
        passed to :func:`~shiny.ui.output_text`.)

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
    * :class:`~shiny.render.code`
    * :func:`~shiny.ui.output_text`
    """

    def auto_output_ui(
        self,
        *,
        inline: bool | MISSING_TYPE = MISSING,
    ) -> Tag:
        kwargs: dict[str, Any] = {}
        set_kwargs_value(kwargs, "inline", inline, self.inline)

        return _ui.output_text(self.output_id, **kwargs)

    def __init__(
        self,
        _fn: Optional[ValueFn[str]] = None,
        *,
        inline: bool = False,
    ) -> None:
        super().__init__(_fn)
        self.inline: bool = inline

    async def transform(self, value: str) -> Jsonifiable:
        return str(value)


# ======================================================================================
# RenderCode
# ======================================================================================


class code(Renderer[str]):
    """
    Reactively render text as code (monospaced).

    When used in Shiny Express applications, this defaults to displaying the text in a
    monospace font in a code block. When used in Shiny Core applications, this should be
    paired with :func:`~shiny.ui.output_code` in the UI.

    Parameters
    ----------
    placeholder
        (Express only) If the output is empty or ``None``, should an empty rectangle be
        displayed to serve as a placeholder? This does not affect behavior when the
        output is nonempty. (This argument is passed to :func:`~shiny.ui.output_code`.)


    Returns
    -------
    :
        A decorator for a function that returns a string.

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_code` container (see :func:`~shiny.ui.output_code` for
    example usage).

    See Also
    --------
    * :class:`~shiny.render.code`
    * :func:`~shiny.ui.output_code`
    """

    def auto_output_ui(
        self,
        *,
        placeholder: bool | MISSING_TYPE = MISSING,
    ) -> Tag:
        kwargs: dict[str, bool] = {}
        set_kwargs_value(kwargs, "placeholder", placeholder, self.placeholder)
        return _ui.output_code(self.output_id, **kwargs)

    def __init__(
        self,
        _fn: Optional[ValueFn[str]] = None,
        *,
        placeholder: bool = True,
    ) -> None:
        super().__init__(_fn)
        self.placeholder = placeholder

    async def transform(self, value: str) -> Jsonifiable:
        return str(value)


# ======================================================================================
# RenderPlot
# ======================================================================================


# It would be nice to specify the return type of ValueFn to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.


@add_example(ex_dir="../api-examples/output_plot")
@no_example("express")
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
    * :func:`~shiny.ui.output_plot`
    * :class:`~shiny.render.image`
    """

    def auto_output_ui(
        self,
        *,
        width: str | float | int | MISSING_TYPE = MISSING,
        height: str | float | int | MISSING_TYPE = MISSING,
        **kwargs: object,
    ) -> Tag:
        # Only set the arg if it is available. (Prevents duplicating default values)
        set_kwargs_value(kwargs, "width", width, self.width)
        set_kwargs_value(kwargs, "height", height, self.height)
        return _ui.output_plot(
            self.output_id,
            # (possibly) contains `width` and `height` keys!
            **kwargs,  # pyright: ignore[reportArgumentType]
        )
        # TODO: Deal with output width/height separately from render width/height?

    def __init__(
        self,
        _fn: Optional[ValueFn[object]] = None,
        *,
        alt: Optional[str] = None,
        width: float | None | MISSING_TYPE = MISSING,
        height: float | None | MISSING_TYPE = MISSING,
        **kwargs: object,
    ) -> None:
        super().__init__(_fn)
        self.alt = alt
        self.width = width
        self.height = height
        self.kwargs = kwargs

    async def render(self) -> dict[str, Jsonifiable] | Jsonifiable | None:
        is_userfn_async = self.fn.is_async()
        session = require_active_session(None)
        # Module support
        output_name = session.ns(self.output_id)
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
            result = inputs[
                ResolvedId(f".clientdata_output_{output_name}_{dimension}")
            ]()
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
        x = await self.fn()

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

        def cast_result(result: ImgData | None) -> dict[str, Jsonifiable] | None:
            if result is None:
                return None
            return imgdata_to_jsonifiable(result)

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
@add_example(ex_dir="../api-examples/output_image")
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
    * :func:`~shiny.ui.output_image`
    * :class:`~shiny.types.ImgData`
    * :class:`~shiny.render.plot`
    """

    def auto_output_ui(self, **kwargs: object):
        return _ui.output_image(
            self.output_id,
            **kwargs,  # pyright: ignore[reportArgumentType]
        )
        # TODO: Make width/height handling consistent with render_plot

    def __init__(
        self,
        _fn: Optional[ValueFn[ImgData]] = None,
        *,
        delete_file: bool = False,
    ) -> None:
        super().__init__(_fn)

        self.delete_file = delete_file

    async def transform(self, value: ImgData) -> dict[str, Jsonifiable] | None:
        src: str = value.get("src")
        try:
            with open(src, "rb") as f:
                data = base64.b64encode(f.read())
                data_str = data.decode("utf-8")
            content_type = _utils.guess_mime_type(src)
            value["src"] = f"data:{content_type};base64,{data_str}"
            return imgdata_to_jsonifiable(value)
        finally:
            if self.delete_file:
                os.remove(src)


# ======================================================================================
# RenderTable
# ======================================================================================


@add_example(ex_dir="../api-examples/output_table")
class table(Renderer[IntoDataFrame]):
    """
    Reactively render a pandas ``DataFrame`` object (or similar) as a basic HTML
    table.

    Consider using :class:`~shiny.render.data_frame` instead of this renderer, as
    it provides high performance virtual scrolling, built-in filtering and sorting,
    and a better default appearance. This renderer may still be helpful if you
    use pandas styling features that are not currently supported by
    :class:`~shiny.render.data_frame`.

    Parameters
    ----------
    index
        Whether to print index (row) labels. (Ignored for pandas :class:`~pandas.io.formats.style.Styler`
        objects; call ``style.hide(axis="index")`` from user code instead.)
    classes
        CSS classes (space separated) to apply to the resulting table. By default, we
        use `table shiny-table w-auto` which is designed to look reasonable with
        Bootstrap 5. (Ignored for pandas :class:`~pandas.io.formats.style.Styler` objects; call
        ``style.set_table_attributes('class="dataframe table shiny-table w-auto"')``
        from user code instead.)
    **kwargs
        Additional keyword arguments passed to ``pandas.DataFrame.to_html()`` or
        ``pandas.io.formats.style.Styler.to_html()``.

    Returns
    -------
    :
        A decorator for a function that returns any of the following:

        1. A pandas :class:`~pandas.DataFrame` object.
        2. A pandas :class:`~pandas.io.formats.style.Styler` object.
        3. Any object that has a `.to_pandas()` method (e.g., a Polars data frame or
           Arrow table).

    Tip
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_table` container (see :func:`~shiny.ui.output_table`
    for example usage).

    See Also
    --------
    * :func:`~shiny.ui.output_table` for the corresponding UI component to this render function.
    """

    def auto_output_ui(self, **kwargs: TagAttrValue) -> Tag:
        return _ui.output_table(self.output_id, **kwargs)
        # TODO: Deal with kwargs

    def __init__(
        self,
        _fn: Optional[ValueFn[IntoDataFrame]] = None,
        *,
        index: bool = False,
        classes: str = "table shiny-table w-auto",
        border: int = 0,
        **kwargs: object,
    ) -> None:
        super().__init__(_fn)
        self.index: bool = index
        self.classes: str = classes
        self.border: int = border
        self.kwargs: dict[str, object] = kwargs

        # TODO: deal with kwargs collision with output_table

    async def transform(self, value: IntoDataFrame) -> dict[str, Jsonifiable]:
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
                try:
                    nw_data = as_data_frame(value)
                except Exception as e:
                    raise TypeError(
                        "@render.table doesn't know how to render objects of type "
                        f"'{str(type(value))}'. Return eager data frames that can "
                        "be handled by `narwhals`."
                    ) from e
                value = nw_data.to_pandas()

            html = cast(  # pyright: ignore[reportUnnecessaryCast]
                str,
                value.to_html(  # pyright: ignore
                    index=self.index,
                    classes=self.classes,
                    border=self.border,
                    **self.kwargs,  # pyright: ignore[reportArgumentType]
                ),
            )
        # Use typing to make sure the return shape matches
        ret: RenderedDeps = {"deps": [], "html": html}
        return rendered_deps_to_jsonifiable(ret)


# ======================================================================================
# RenderUI
# ======================================================================================
@add_example(ex_dir="../api-examples/output_ui")
class ui(Renderer[TagChild]):
    """
    Reactively render HTML content.

    Note: If you want to write your function with Shiny Express syntax, where the UI
    components are automatically captured as the code is evaluated, use
    :func:`~shiny.express.render.express` instead of this function.

    This function is used to render HTML content, but it requires that the funciton
    returns the content, using Shiny Core syntax.

    Returns
    -------
    :
        A decorator for a function that returns an object of type
        :class:`~htmltools.TagChild`.

    Tips
    ----
    The name of the decorated function (or ``@output(id=...)``) should match the ``id``
    of a :func:`~shiny.ui.output_ui` container (see :func:`~shiny.ui.output_ui` for
    example usage).

    See Also
    --------
    * :func:`~shiny.express.render.express`
    * :func:`~shiny.express.expressify`
    * :func:`~shiny.ui.output_ui`
    """

    def auto_output_ui(self) -> Tag:
        return _ui.output_ui(self.output_id)

    async def transform(self, value: TagChild) -> Jsonifiable:
        session = require_active_session(None)
        return rendered_deps_to_jsonifiable(
            session._process_ui(value),
        )


# ======================================================================================
# RenderDownload
# ======================================================================================
@add_example(ex_dir="../api-examples/download")
class download(Renderer[str]):
    """
    Decorator to register a function to handle a download.

    This decorator is used to register a function that will be called when the user
    clicks a download link or button. The decorated function may be sync or async, and
    should do one of the following:

    * Return a string. This will be assumed to be a filename; Shiny will return this
      file to the browser, and the downloaded file will have the same filename as the
      original, with an inferred mime type. This is the most convenient IF the file
      already exists on disk. But if the function must create a temporary file, then
      this method should not be used, because the temporary file will not be deleted by
      Shiny. Use the `yield` method instead.
    * `yield` one or more strings or bytestrings (`b"..."` or
      `io.BytesIO().getvalue()`). If strings are yielded, they'll be encoded in UTF-8.
      (This is better for temp files as after you're done yielding you can delete the
      temp file, or use a tempfile.TemporaryFile context manager) With this method, it's
      important that the `@render.download` decorator have a `filename` argument, as the
      decorated function won't help with that.

    Parameters
    ----------
    filename
        The filename of the download.
    media_type
        The media type of the download.
    encoding
        The encoding of the download.
    label
        (Express only) A label for the button. Defaults to "Download".

    Returns
    -------
    :
        The decorated function.

    See Also
    --------
    * :func:`~shiny.ui.download_button`
    * :func:`~shiny.ui.download_link`
    """

    def auto_output_ui(self) -> Tag:
        return _ui.download_button(
            self.output_id,
            label=self.label,
        )

    def __init__(
        self,
        fn: Optional[DownloadHandler] = None,
        *,
        filename: Optional[str | Callable[[], str]] = None,
        media_type: None | str | Callable[[], str] = None,
        encoding: str = "utf-8",
        label: TagChild = "Download",
    ) -> None:
        super().__init__()

        self.filename = filename
        self.media_type = media_type
        self.encoding = encoding
        self.label = label

        if fn is not None:
            self(fn)

    def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        fn: DownloadHandler,
    ) -> Self:
        # For downloads, the value function (which is passed to `__call__()`) is
        # different than for other renderers. For normal renderers, the user supplies
        # the value function. This function returns a value which is transformed,
        # serialized to JSON, and then sent to the browser.
        #
        # For downloads, the download button itself is actually an output. The value
        # that it renders is a URL; when the user clicks the button, the browser
        # initiates a download from that URL, and the server provides the file via
        # `session._downloads`.
        #
        # The `url()` function here is the value function for the download button. It
        # returns the URL for downloading the file.
        def url() -> str:
            from urllib.parse import quote

            session = require_active_session(None)
            # All download urls must be fully namespaced
            return f"session/{quote(session.id)}/download/{quote(session.ns(self.output_id))}?w="

        # Unlike most value functions, this one's name is `url`. But we want to get the
        # name from the user-supplied function.
        url.__name__ = fn.__name__

        # We invoke `super().__call__()` now, because it indirectly invokes
        # `Outputs.__call__()`, which sets `output_id` (and `self.__name__`), which is
        # then used below.
        super().__call__(url)

        # Register the download handler for the session. The reason we check for session
        # not being None or a stub session is because in Express, when the UI is
        # rendered, this function `render.download()()`  called once before any sessions
        # have been started.
        session = get_current_session()
        if session is not None and not session.is_stub_session():
            # All download objects are stored in the root session.
            # They must be fully namespaced
            session._downloads[session.ns(self.output_id)] = DownloadInfo(
                filename=self.filename,
                content_type=self.media_type,
                handler=fn,
                encoding=self.encoding,
            )

        return self

    async def transform(self, value: str) -> Jsonifiable:
        return value
