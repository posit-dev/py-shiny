__all__ = (
    "render_text",
    "render_plot",
    "render_image",
    "render_ui",
)

import sys
import os
import io
import base64
import mimetypes
from typing import TYPE_CHECKING, Callable, Optional, Awaitable, Union
import typing

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from htmltools import TagChildArg

if TYPE_CHECKING:
    from .session import Session

from . import utils


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
        self._fn: RenderTextFuncAsync = utils.wrap_async(fn)

    def __call__(self) -> Union[str, None]:
        return utils.run_coro_sync(self.run())

    async def run(self) -> Union[str, None]:
        return await self._fn()


class RenderTextAsync(RenderText, RenderFunctionAsync):
    def __init__(self, fn: RenderTextFuncAsync) -> None:
        if not utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderTextFunc, fn))

    async def __call__(self) -> Union[str, None]:  # type: ignore
        return await self.run()


def render_text() -> Callable[[Union[RenderTextFunc, RenderTextFuncAsync]], RenderText]:
    def wrapper(fn: Union[RenderTextFunc, RenderTextFuncAsync]) -> RenderText:
        if utils.is_async_callable(fn):
            return RenderTextAsync(fn)
        else:
            fn = typing.cast(RenderTextFunc, fn)
            return RenderText(fn)

    return wrapper


# ======================================================================================
# RenderPlot
# ======================================================================================
# It would be nice to specify the return type of RenderPlotFunc to be something like:
#   Union[matplotlib.figure.Figure, PIL.Image.Image]
# However, if we did that, we'd have to import those modules at load time, which adds
# a nontrivial amount of overhead. So for now, we're just using `object`.
RenderPlotFunc = Callable[[], object]
RenderPlotFuncAsync = Callable[[], Awaitable[object]]


class ImgData(TypedDict):
    src: str
    width: Union[str, float]
    height: Union[str, float]
    alt: Optional[str]


class RenderPlot(RenderFunction):
    _ppi: float = 96

    def __init__(self, fn: RenderPlotFunc, *, alt: Optional[str] = None) -> None:
        super().__init__(fn)
        self._alt: Optional[str] = alt
        # The Render*Async subclass will pass in an async function, but it tells the
        # static type checker that it's synchronous. wrap_async() is smart -- if is
        # passed an async function, it will not change it.
        self._fn: RenderPlotFuncAsync = utils.wrap_async(fn)

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
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

        fig = await self._fn()

        if fig is None:
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
        result: Union[ImgData, None, Literal["TYPE_MISMATCH"]] = None
        if "matplotlib" in sys.modules:
            result = try_render_plot_matplotlib(
                fig, width, height, pixelratio, self._ppi
            )
            if result != "TYPE_MISMATCH":
                return result

        if "PIL" in sys.modules:
            result = try_render_plot_pil(fig, width, height, pixelratio, self._ppi)
            if result != "TYPE_MISMATCH":
                return result

        raise Exception("Unsupported figure type: " + str(type(fig)))


class RenderPlotAsync(RenderPlot, RenderFunctionAsync):
    def __init__(self, fn: RenderPlotFuncAsync, alt: Optional[str] = None) -> None:
        if not utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderPlotFunc, fn), alt=alt)

    async def __call__(self) -> object:
        return await self.run()


# TODO: Use more specific types for render_plot
def render_plot(
    alt: Optional[str] = None,
) -> Callable[[Union[RenderPlotFunc, RenderPlotFuncAsync]], RenderPlot]:
    def wrapper(fn: Union[RenderPlotFunc, RenderPlotFuncAsync]) -> RenderPlot:
        if utils.is_async_callable(fn):
            return RenderPlotAsync(fn, alt=alt)
        else:
            return RenderPlot(fn, alt=alt)

    return wrapper


# Try to render a matplotlib object. If `fig` is not a matplotlib object, return
# "TYPE_MISMATCH". If there's an error in rendering, return None. If successful in
# rendering, return an ImgData object.
def try_render_plot_matplotlib(
    fig: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
) -> Union[ImgData, None, Literal["TYPE_MISMATCH"]]:
    import matplotlib.figure
    import matplotlib.pyplot

    if isinstance(fig, matplotlib.figure.Figure):
        try:
            fig.set_dpi(ppi * pixelratio)
            fig.set_size_inches(width / ppi, height / ppi)

            with io.BytesIO() as buf:
                fig.savefig(buf, format="png")
                buf.seek(0)
                data = base64.b64encode(buf.read())
                data_str = data.decode("utf-8")

            res: ImgData = {
                "src": "data:image/png;base64," + data_str,
                "width": width,
                "height": height,
                "alt": alt,
            }

            return res

        except Exception as e:
            # TODO: just let errors propagate?
            print("Error rendering matplotlib object: " + str(e))

        finally:
            matplotlib.pyplot.close(fig)

        return None

    else:
        return "TYPE_MISMATCH"


def try_render_plot_pil(
    fig: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
) -> Union[ImgData, None, Literal["TYPE_MISMATCH"]]:
    import PIL.Image

    if isinstance(fig, PIL.Image.Image):
        try:
            with io.BytesIO() as buf:
                fig.save(buf, format="PNG")
                buf.seek(0)
                data = base64.b64encode(buf.read())
                data_str = data.decode("utf-8")

            res: ImgData = {
                "src": "data:image/png;base64," + data_str,
                "width": width,
                "height": height,
                "alt": alt,
            }

            return res

        except Exception as e:
            # TODO: just let errors propagate?
            print("Error rendering PIL object: " + str(e))

        return None

    else:
        return "TYPE_MISMATCH"


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
        self._fn: RenderImageFuncAsync = utils.wrap_async(fn)

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
        res: ImgData = await self._fn()
        src: str = res.get("src")
        try:
            with open(src, "rb") as f:
                data = base64.b64encode(f.read())
                data_str = data.decode("utf-8")
            content_type = mimetypes.guess_type(src)[1]
            res["src"] = f"data:{content_type};base64,{data_str}"
            return res
        finally:
            if self._delete_file:
                os.remove(src)


class RenderImageAsync(RenderImage, RenderFunctionAsync):
    def __init__(self, fn: RenderImageFuncAsync, delete_file: bool = False) -> None:
        if not utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderImageFunc, fn), delete_file=delete_file)

    async def __call__(self) -> object:
        return await self.run()


def render_image(
    delete_file: bool = False,
) -> Callable[[Union[RenderImageFunc, RenderImageFuncAsync]], RenderImage]:
    def wrapper(fn: Union[RenderImageFunc, RenderImageFuncAsync]) -> RenderImage:
        if utils.is_async_callable(fn):
            return RenderImageAsync(fn, delete_file=delete_file)
        else:
            fn = typing.cast(RenderImageFunc, fn)
            return RenderImage(fn, delete_file=delete_file)

    return wrapper


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
        self._fn: RenderUIFuncAsync = utils.wrap_async(fn)

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
        ui: TagChildArg = await self._fn()
        if ui is None:
            return None
        # TODO: better a better workaround for the circular dependency
        from .session import _process_deps

        return _process_deps(ui, self._session)


class RenderUIAsync(RenderUI, RenderFunctionAsync):
    def __init__(self, fn: RenderUIFuncAsync) -> None:
        if not utils.is_async_callable(fn):
            raise TypeError(self.__class__.__name__ + " requires an async function")
        super().__init__(typing.cast(RenderUIFunc, fn))

    async def __call__(self) -> object:
        return await self.run()


def render_ui() -> Callable[[Union[RenderUIFunc, RenderUIFuncAsync]], RenderUI]:
    def wrapper(
        fn: Union[Callable[[], TagChildArg], Callable[[], Awaitable[TagChildArg]]]
    ) -> RenderUI:
        if utils.is_async_callable(fn):
            return RenderUIAsync(fn)
        else:
            fn = typing.cast(RenderUIFunc, fn)
            return RenderUI(fn)

    return wrapper
