# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

__all__ = (
    "RenderFunction",
    "RenderFunctionAsync",
    "RenderText",
    "RenderTextAsync",
    "text",
    "RenderPlot",
    "RenderPlotAsync",
    "plot",
    "RenderImage",
    "RenderImageAsync",
    "image",
    "RenderTable",
    "RenderTableAsync",
    "table",
    "RenderUI",
    "RenderUIAsync",
    "ui",
)

import base64
import os
import sys
import typing
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

# These aren't used directly in this file, but they seem necessary for Sphinx to work
# cleanly.
from htmltools import Tag  # pyright: ignore[reportUnusedImport] # noqa: F401
from htmltools import Tagifiable  # pyright: ignore[reportUnusedImport] # noqa: F401
from htmltools import TagList  # pyright: ignore[reportUnusedImport] # noqa: F401
from htmltools import TagChild

if TYPE_CHECKING:
    from ..session import Session
    from ..session._utils import RenderedDeps
    import pandas as pd

from typing import Protocol, runtime_checkable

from .. import _utils
from .._namespaces import ResolvedId
from ..types import ImgData
from ._try_render_plot import try_render_matplotlib, try_render_pil, try_render_plotnine

# Input type for the user-spplied function that is passed to a render.xx
IT = TypeVar("IT")
# Output type after the RenderFunction.__call__ method is called on the IT object.
OT = TypeVar("OT")


# ======================================================================================
# RenderFunction/RenderFunctionAsync base class
# ======================================================================================


# A RenderFunction object is given a user-provided function which returns an IT. When
# the .__call___ method is invoked, it calls the user-provided function (which returns
# an IT), then converts the IT to an OT. Note that in many cases but not all, IT and OT
# will be the same.
class RenderFunction(Generic[IT, OT]):
    def __init__(self, fn: Callable[[], IT]) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

    def __call__(self) -> OT:
        raise NotImplementedError

    def set_metadata(self, session: Session, name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session: Session = session
        self._name: str = name


# The reason for having a separate RenderFunctionAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RenderFunctionAsync(RenderFunction[IT, OT]):
    async def __call__(self) -> OT:  # pyright: ignore[reportIncompatibleMethodOverride]
        raise NotImplementedError


# ======================================================================================
# RenderText
# ======================================================================================
RenderTextFunc = Callable[[], "str | None"]
RenderTextFuncAsync = Callable[[], Awaitable["str | None"]]


class RenderText(RenderFunction["str | None", "str | None"]):
    def __init__(self, fn: RenderTextFunc) -> None:
        super().__init__(fn)
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderTextFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> str | None:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> str | None:
        res = await self._fn()
        if res is None:
            return None
        return str(res)


class RenderTextAsync(RenderText, RenderFunctionAsync["str | None", "str | None"]):
    def __init__(self, fn: RenderTextFuncAsync) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderTextFunc, fn))

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> str | None:
        return await self._run()


@overload
def text(fn: RenderTextFunc | RenderTextFuncAsync) -> RenderText:
    ...


@overload
def text() -> Callable[[RenderTextFunc | RenderTextFuncAsync], RenderText]:
    ...


def text(
    fn: Optional[RenderTextFunc | RenderTextFuncAsync] = None,
) -> RenderText | Callable[[RenderTextFunc | RenderTextFuncAsync], RenderText]:
    """
    Reactively render text.

    Returns
    -------
    :
        A decorator for a function that returns a string.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_text` container (see :func:`~shiny.ui.output_text` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_text
    """

    def wrapper(fn: RenderTextFunc | RenderTextFuncAsync) -> RenderText:
        if _utils.is_async_callable(fn):
            return RenderTextAsync(fn)
        else:
            fn = typing.cast(RenderTextFunc, fn)
            return RenderText(fn)

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)


# ======================================================================================
# RenderPlot
# ======================================================================================
# It would be nice to specify the return type of RenderPlotFunc to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.
RenderPlotFunc = Callable[[], object]
RenderPlotFuncAsync = Callable[[], Awaitable[object]]


class RenderPlot(RenderFunction[object, "ImgData | None"]):
    _ppi: float = 96
    _is_userfn_async = False

    def __init__(
        self, fn: RenderPlotFunc, *, alt: Optional[str] = None, **kwargs: object
    ) -> None:
        super().__init__(fn)
        self._alt: Optional[str] = alt
        self._kwargs = kwargs
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderPlotFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> ImgData | None:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> ImgData | None:
        inputs = self._session.root_scope().input

        # Reactively read some information about the plot.
        pixelratio: float = typing.cast(
            float, inputs[ResolvedId(".clientdata_pixelratio")]()
        )
        width: float = typing.cast(
            float, inputs[ResolvedId(f".clientdata_output_{self._name}_width")]()
        )
        height: float = typing.cast(
            float, inputs[ResolvedId(f".clientdata_output_{self._name}_height")]()
        )

        x = await self._fn()

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
                x, width, height, pixelratio, self._ppi, **self._kwargs
            )
            if ok:
                return result

        if "matplotlib" in sys.modules:
            ok, result = try_render_matplotlib(
                x,
                width,
                height,
                pixelratio=pixelratio,
                ppi=self._ppi,
                allow_global=not self._is_userfn_async,
                alt=self._alt,
                **self._kwargs,
            )
            if ok:
                return result

        if "PIL" in sys.modules:
            ok, result = try_render_pil(
                x, width, height, pixelratio, self._ppi, **self._kwargs
            )
            if ok:
                return result

        # This check must happen last because matplotlib might be able to plot even if
        # x is None
        if x is None:
            return None

        raise Exception(
            f"@render.plot doesn't know to render objects of type '{str(type(x))}'. "
            + "Consider either requesting support for this type of plot object, and/or "
            + " explictly saving the object to a (png) file and using @render.image."
        )


class RenderPlotAsync(RenderPlot, RenderFunctionAsync[object, "ImgData | None"]):
    _is_userfn_async = True

    def __init__(
        self, fn: RenderPlotFuncAsync, alt: Optional[str] = None, **kwargs: Any
    ) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderPlotFunc, fn), alt=alt, **kwargs)

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> ImgData | None:
        return await self._run()


@overload
def plot(fn: RenderPlotFunc | RenderPlotFuncAsync) -> RenderPlot:
    ...


@overload
def plot(
    *,
    alt: Optional[str] = None,
    **kwargs: Any,
) -> Callable[[RenderPlotFunc | RenderPlotFuncAsync], RenderPlot]:
    ...


# TODO: Use more specific types for render.plot
def plot(
    fn: Optional[RenderPlotFunc | RenderPlotFuncAsync] = None,
    *,
    alt: Optional[str] = None,
    **kwargs: Any,
) -> RenderPlot | Callable[[RenderPlotFunc | RenderPlotFuncAsync], RenderPlot]:
    """
    Reactively render a plot object as an HTML image.

    Parameters
    ----------
    alt
        Alternative text for the image if it cannot be displayed or viewed (i.e., the
        user uses a screen reader).
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
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of a
    :func:`~shiny.ui.output_plot` container (see :func:`~shiny.ui.output_plot` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_plot
    ~shiny.render.image
    """

    def wrapper(fn: RenderPlotFunc | RenderPlotFuncAsync) -> RenderPlot:
        if _utils.is_async_callable(fn):
            return RenderPlotAsync(fn, alt=alt, **kwargs)
        else:
            return RenderPlot(fn, alt=alt, **kwargs)

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)


# ======================================================================================
# RenderImage
# ======================================================================================
RenderImageFunc = Callable[[], "ImgData | None"]
RenderImageFuncAsync = Callable[[], Awaitable["ImgData | None"]]


class RenderImage(RenderFunction["ImgData | None", "ImgData | None"]):
    def __init__(
        self,
        fn: RenderImageFunc,
        *,
        delete_file: bool = False,
    ) -> None:
        super().__init__(fn)
        self._delete_file: bool = delete_file
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderImageFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> ImgData | None:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> ImgData | None:
        res: ImgData | None = await self._fn()
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
            if self._delete_file:
                os.remove(src)


class RenderImageAsync(
    RenderImage, RenderFunctionAsync["ImgData | None", "ImgData | None"]
):
    def __init__(self, fn: RenderImageFuncAsync, delete_file: bool = False) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderImageFunc, fn), delete_file=delete_file)

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> ImgData | None:
        return await self._run()


@overload
def image(fn: RenderImageFunc | RenderImageFuncAsync) -> RenderImage:
    ...


@overload
def image(
    *,
    delete_file: bool = False,
) -> Callable[[RenderImageFunc | RenderImageFuncAsync], RenderImage]:
    ...


def image(
    fn: Optional[RenderImageFunc | RenderImageFuncAsync] = None,
    *,
    delete_file: bool = False,
) -> RenderImage | Callable[[RenderImageFunc | RenderImageFuncAsync], RenderImage]:
    """
    Reactively render a image file as an HTML image.

    Parameters
    ----------
    delete_file
        If ``True``, the image file will be deleted after rendering.

    Returns
    -------
    :
        A decorator for a function that returns an `~shiny.types.ImgData` object.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_image` container (see :func:`~shiny.ui.output_image` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_image
    ~shiny.types.ImgData
    ~shiny.render.plot
    """

    def wrapper(fn: RenderImageFunc | RenderImageFuncAsync) -> RenderImage:
        if _utils.is_async_callable(fn):
            return RenderImageAsync(fn, delete_file=delete_file)
        else:
            fn = typing.cast(RenderImageFunc, fn)
            return RenderImage(fn, delete_file=delete_file)

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)


# ======================================================================================
# RenderTable
# ======================================================================================


@runtime_checkable
class PandasCompatible(Protocol):
    # Signature doesn't matter, runtime_checkable won't look at it anyway
    def to_pandas(self) -> "pd.DataFrame":
        ...


TableResult = Union[None, "pd.DataFrame", PandasCompatible]
RenderTableFunc = Callable[[], TableResult]
RenderTableFuncAsync = Callable[[], Awaitable[TableResult]]


class RenderTable(RenderFunction[object, "RenderedDeps | None"]):
    def __init__(
        self,
        fn: RenderTableFunc,
        *,
        index: bool = False,
        classes: str = "table shiny-table w-auto",
        border: int = 0,
        **kwargs: object,
    ) -> None:
        super().__init__(fn)
        self._index = index
        self._classes = classes
        self._border = border
        self._kwargs = kwargs
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderTableFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> RenderedDeps | None:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> RenderedDeps | None:
        x = await self._fn()

        if x is None:
            return None

        import pandas
        import pandas.io.formats.style

        html: str
        if isinstance(x, pandas.io.formats.style.Styler):
            html = x.to_html(**self._kwargs)  # pyright: ignore[reportUnknownMemberType]
        else:
            if not isinstance(x, pandas.DataFrame):
                if not isinstance(x, PandasCompatible):
                    raise TypeError(
                        "@render.table doesn't know how to render objects of type "
                        f"'{str(type(x))}'. Return either a pandas.DataFrame, or an object "
                        "that has a .to_pandas() method."
                    )
                x = x.to_pandas()

            html = x.to_html(  # pyright: ignore[reportUnknownMemberType]
                index=self._index,
                classes=self._classes,
                border=self._border,
                **self._kwargs,
            )
        return {"deps": [], "html": html}


class RenderTableAsync(RenderTable, RenderFunctionAsync[object, "ImgData | None"]):
    def __init__(
        self,
        fn: RenderTableFuncAsync,
        *,
        index: bool = False,
        classes: str = "table shiny-table w-auto",
        border: int = 0,
        **kwargs: Any,
    ) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(
            typing.cast(RenderTableFunc, fn),
            index=index,
            classes=classes,
            border=border,
            **kwargs,
        )

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> RenderedDeps | None:
        return await self._run()


@overload
def table(fn: RenderTableFunc | RenderTableFuncAsync) -> RenderTable:
    ...


@overload
def table(
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: Any,
) -> Callable[[RenderTableFunc | RenderTableFuncAsync], RenderTable]:
    ...


# TODO: Use more specific types for render.table
def table(
    fn: Optional[RenderTableFunc | RenderTableFuncAsync] = None,
    *,
    index: bool = False,
    classes: str = "table shiny-table w-auto",
    border: int = 0,
    **kwargs: Any,
) -> RenderTable | Callable[[RenderTableFunc | RenderTableFuncAsync], RenderTable]:
    """
    Reactively render a Pandas data frame object (or similar) as a basic HTML table.

    Consider using ~shiny.render.data_frame instead of this renderer, as it provides
    high performance virtual scrolling, built-in filtering and sorting, and a better
    default appearance. This renderer may still be helpful if you use pandas styling
    features that are not currently supported by ~shiny.render.data_frame.

    Parameters
    ----------
    index
        Whether to print index (row) labels. (Ignored for pandas :class:`Styler`
        objects; call ``style.hide(axis="index")`` from user code instead.)
    classes
        CSS classes (space separated) to apply to the resulting table. By default, we
        use `table shiny-table w-auto` which is designed to look reasonable with Bootstrap 5.
        (Ignored for pandas :class:`Styler` objects; call
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
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_table` container (see :func:`~shiny.ui.output_table` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_table for the corresponding UI component to this render function.
    """

    def wrapper(fn: RenderTableFunc | RenderTableFuncAsync) -> RenderTable:
        if _utils.is_async_callable(fn):
            return RenderTableAsync(
                fn, index=index, classes=classes, border=border, **kwargs
            )
        else:
            return RenderTable(
                cast(RenderTableFunc, fn),
                index=index,
                classes=classes,
                border=border,
                **kwargs,
            )

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)


# ======================================================================================
# RenderUI
# ======================================================================================
RenderUIFunc = Callable[[], TagChild]
RenderUIFuncAsync = Callable[[], Awaitable[TagChild]]


class RenderUI(RenderFunction[TagChild, "RenderedDeps | None"]):
    def __init__(self, fn: RenderUIFunc) -> None:
        super().__init__(fn)
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderUIFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> RenderedDeps | None:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> RenderedDeps | None:
        ui: TagChild = await self._fn()
        if ui is None:
            return None

        return self._session._process_ui(ui)


class RenderUIAsync(RenderUI, RenderFunctionAsync[TagChild, "RenderedDeps| None"]):
    def __init__(self, fn: RenderUIFuncAsync) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderUIFunc, fn))

    async def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> RenderedDeps | None:
        return await self._run()


@overload
def ui(fn: RenderUIFunc | RenderUIFuncAsync) -> RenderUI:
    ...


@overload
def ui() -> Callable[[RenderUIFunc | RenderUIFuncAsync], RenderUI]:
    ...


def ui(
    fn: Optional[RenderUIFunc | RenderUIFuncAsync] = None,
) -> RenderUI | Callable[[RenderUIFunc | RenderUIFuncAsync], RenderUI]:
    """
    Reactively render HTML content.

    Returns
    -------
    :
        A decorator for a function that returns an object of type `~shiny.ui.TagChild`.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_ui` container (see :func:`~shiny.ui.output_ui` for example
    usage).

    See Also
    --------
    ~shiny.ui.output_ui
    """

    def wrapper(
        fn: Callable[[], TagChild] | Callable[[], Awaitable[TagChild]]
    ) -> RenderUI:
        if _utils.is_async_callable(fn):
            return RenderUIAsync(fn)
        else:
            fn = typing.cast(RenderUIFunc, fn)
            return RenderUI(fn)

    if fn is None:
        return wrapper
    else:
        return wrapper(fn)
