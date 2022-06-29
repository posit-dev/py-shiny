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
    "RenderUI",
    "RenderUIAsync",
    "ui",
)

import base64
import os
import sys
import typing
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Union, overload

from htmltools import TagChildArg

if TYPE_CHECKING:
    from ..session import Session

from .. import _utils
from ..types import ImgData
from ._try_render_plot import (
    TryPlotResult,
    try_render_matplotlib,
    try_render_pil,
    try_render_plotnine,
)


# ======================================================================================
# RenderFunction/RenderFunctionAsync base class
# ======================================================================================
class RenderFunction:
    def __init__(self, fn: Callable[[], object]) -> None:
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

    def __call__(self) -> object:
        raise NotImplementedError

    def set_metadata(self, session: "Session", name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session: Session = session
        self._name: str = name


# The reason for having a separate RenderFunctionAsync class is because the __call__
# method is marked here as async; you can't have a single class where one method could
# be either sync or async.
class RenderFunctionAsync(RenderFunction):
    async def __call__(self) -> object:
        raise NotImplementedError


# ======================================================================================
# RenderText
# ======================================================================================
RenderTextFunc = Callable[[], Union[str, None]]
RenderTextFuncAsync = Callable[[], Awaitable[Union[str, None]]]


class RenderText(RenderFunction):
    def __init__(self, fn: RenderTextFunc) -> None:
        super().__init__(fn)
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderTextFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> Union[str, None]:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> Union[str, None]:
        res = await self._fn()
        if res is None:
            return None
        return str(res)


class RenderTextAsync(RenderText, RenderFunctionAsync):
    def __init__(self, fn: RenderTextFuncAsync) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderTextFunc, fn))

    async def __call__(self) -> Union[str, None]:  # type: ignore
        return await self._run()


@overload
def text(fn: Union[RenderTextFunc, RenderTextFuncAsync]) -> RenderText:
    ...


@overload
def text() -> Callable[[Union[RenderTextFunc, RenderTextFuncAsync]], RenderText]:
    ...


def text(
    fn: Optional[Union[RenderTextFunc, RenderTextFuncAsync]] = None
) -> Union[
    RenderText, Callable[[Union[RenderTextFunc, RenderTextFuncAsync]], RenderText]
]:
    """
    Reactively render text.

    Returns
    -------
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

    def wrapper(fn: Union[RenderTextFunc, RenderTextFuncAsync]) -> RenderText:
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


class RenderPlot(RenderFunction):
    _ppi: float = 96

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

    def __call__(self) -> object:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> object:
        # Reactively read some information about the plot.
        pixelratio: float = typing.cast(
            float, self._session.input[".clientdata_pixelratio"]()
        )
        width: float = typing.cast(
            float, self._session.input[f".clientdata_output_{self._name}_width"]()
        )
        height: float = typing.cast(
            float, self._session.input[f".clientdata_output_{self._name}_height"]()
        )

        x = await self._fn()

        if x is None:
            return None

        # Try each type of renderer in turn. The reason we do it this way is to avoid
        # importing modules that aren't already loaded. That could slow things down, or
        # worse, cause an error if the module isn't installed.
        #
        # Each try_render function should return either an ImgResult, None (which
        # indicates that the rendering failed), or the string "TYPE_MISMATCH" (which
        # indicate that `fig` object was not the type of object that the renderer knows
        # how to handle). In the case of a "TYPE_MISMATCH", it will move on to the next
        # renderer.
        result: TryPlotResult = None

        if "plotnine" in sys.modules:
            result = try_render_plotnine(
                x, width, height, pixelratio, self._ppi, **self._kwargs
            )
            if result != "TYPE_MISMATCH":
                return result

        if "matplotlib" in sys.modules:
            result = try_render_matplotlib(
                x, width, height, pixelratio, self._ppi, **self._kwargs
            )
            if result != "TYPE_MISMATCH":
                return result

        if "PIL" in sys.modules:
            result = try_render_pil(
                x, width, height, pixelratio, self._ppi, **self._kwargs
            )
            if result != "TYPE_MISMATCH":
                return result

        raise Exception(
            f"@render.plot doesn't know to render objects of type '{str(type(x))}'. "
            + "Consider either requesting support for this type of plot object, and/or "
            + " explictly saving the object to a (png) file and using @render.image."
        )


class RenderPlotAsync(RenderPlot, RenderFunctionAsync):
    def __init__(self, fn: RenderPlotFuncAsync, alt: Optional[str] = None) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderPlotFunc, fn), alt=alt)

    async def __call__(self) -> object:
        return await self._run()


@overload
def plot(fn: Union[RenderPlotFunc, RenderPlotFuncAsync]) -> RenderPlot:
    ...


@overload
def plot(
    *,
    alt: Optional[str] = None,
    **kwargs: Any,
) -> Callable[[Union[RenderPlotFunc, RenderPlotFuncAsync]], RenderPlot]:
    ...


# TODO: Use more specific types for render.plot
def plot(
    fn: Optional[Union[RenderPlotFunc, RenderPlotFuncAsync]] = None,
    *,
    alt: Optional[str] = None,
    **kwargs: Any,
) -> Union[
    RenderPlot, Callable[[Union[RenderPlotFunc, RenderPlotFuncAsync]], RenderPlot]
]:
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
    A decorator for a function that returns any of the following:
        1. A :class:`matplotlib.figure.Figure` instance.
        2. An :class:`matplotlib.artist.Artist` instance.
        3. A list/tuple of Figure/Artist instances.
        4. An object with a 'figure' attribute pointing to a
          :class:`matplotlib.figure.Figure` instance.
        5. A :class:`PIL.Image.Image` instance.

    Tip
    ----
    This decorator should be applied **before** the ``@output`` decorator. Also, the
    name of the decorated function (or ``@output(id=...)``) should match the ``id`` of
    a :func:`~shiny.ui.output_plot` container (see :func:`~shiny.ui.output_plot` for
    example usage).

    See Also
    --------
    ~shiny.ui.output_plot
    ~shiny.render.image
    """

    def wrapper(fn: Union[RenderPlotFunc, RenderPlotFuncAsync]) -> RenderPlot:
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
RenderImageFunc = Callable[[], ImgData]
RenderImageFuncAsync = Callable[[], Awaitable[ImgData]]


class RenderImage(RenderFunction):
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

    def __call__(self) -> object:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> object:
        res: ImgData = await self._fn()
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


class RenderImageAsync(RenderImage, RenderFunctionAsync):
    def __init__(self, fn: RenderImageFuncAsync, delete_file: bool = False) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderImageFunc, fn), delete_file=delete_file)

    async def __call__(self) -> object:
        return await self._run()


@overload
def image(fn: Union[RenderImageFunc, RenderImageFuncAsync]) -> RenderImage:
    ...


@overload
def image(
    *,
    delete_file: bool = False,
) -> Callable[[Union[RenderImageFunc, RenderImageFuncAsync]], RenderImage]:
    ...


def image(
    fn: Optional[Union[RenderImageFunc, RenderImageFuncAsync]] = None,
    *,
    delete_file: bool = False,
) -> Union[
    RenderImage, Callable[[Union[RenderImageFunc, RenderImageFuncAsync]], RenderImage]
]:
    """
    Reactively render a image file as an HTML image.

    Parameters
    ----------
    delete_file
        If ``True``, the image file will be deleted after rendering.

    Returns
    -------
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

    def wrapper(fn: Union[RenderImageFunc, RenderImageFuncAsync]) -> RenderImage:
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
# RenderUI
# ======================================================================================
RenderUIFunc = Callable[[], TagChildArg]
RenderUIFuncAsync = Callable[[], Awaitable[TagChildArg]]


class RenderUI(RenderFunction):
    def __init__(self, fn: RenderUIFunc) -> None:
        super().__init__(fn)
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderUIFuncAsync = _utils.wrap_async(fn)

    def __call__(self) -> object:
        return _utils.run_coro_sync(self._run())

    async def _run(self) -> object:
        ui: TagChildArg = await self._fn()
        if ui is None:
            return None

        return self._session._process_ui(ui)


class RenderUIAsync(RenderUI, RenderFunctionAsync):
    def __init__(self, fn: RenderUIFuncAsync) -> None:
        if not _utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderUIFunc, fn))

    async def __call__(self) -> object:
        return await self._run()


@overload
def ui(fn: Union[RenderUIFunc, RenderUIFuncAsync]) -> RenderUI:
    ...


@overload
def ui() -> Callable[[Union[RenderUIFunc, RenderUIFuncAsync]], RenderUI]:
    ...


def ui(
    fn: Optional[Union[RenderUIFunc, RenderUIFuncAsync]] = None
) -> Union[RenderUI, Callable[[Union[RenderUIFunc, RenderUIFuncAsync]], RenderUI]]:
    """
    Reactively render HTML content.

    Returns
    -------
    A decorator for a function that returns an object of type `~shiny.ui.TagChildArg`.

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
        fn: Union[Callable[[], TagChildArg], Callable[[], Awaitable[TagChildArg]]]
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
