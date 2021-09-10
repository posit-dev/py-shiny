import os
import tempfile
import base64
import matplotlib.figure
import matplotlib.pyplot
import inspect
from typing import TYPE_CHECKING, Callable, Optional, Awaitable, Union
import typing
if TYPE_CHECKING:
    from .shinysession import ShinySession

from . import utils


UserRenderFunction = Callable[[], object]
UserRenderFunctionAsync = Callable[[], Awaitable[object]]


class RenderFunction:
    def __init__(self, fn: UserRenderFunction) -> None:
        raise NotImplementedError

    def __call__(self) -> object:
        raise NotImplementedError

    def set_metadata(self, session: 'ShinySession', name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session: ShinySession = session
        self._name: str = name


class RenderFunctionAsync(RenderFunction):
    async def __call__(self) -> object:
        raise NotImplementedError


class Plot(RenderFunction):
    _ppi: float = 96

    def __init__(self, fn: UserRenderFunction, alt: Optional[str] = None) -> None:
        self._fn: UserRenderFunctionAsync = utils.wrap_async(fn)
        self._alt: Optional[str] = alt

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
        # Reactively read some information about the plot.
        pixelratio: float = typing.cast(float, self._session.input[f".clientdata_pixelratio"])
        width: float = typing.cast(float, self._session.input[f".clientdata_output_{self._name}_width"])
        height: float = typing.cast(float, self._session.input[f".clientdata_output_{self._name}_height"])

        fig = await self._fn()

        if (isinstance(fig, matplotlib.figure.Figure)):
            tmpfile = tempfile.mkstemp(suffix = ".png")[1]

            try:
                ppi = self._ppi * pixelratio
                fig.set_dpi(ppi)
                fig.set_size_inches(width / self._ppi, height / self._ppi)

                fig.savefig(tmpfile)

                with open(tmpfile, "rb") as image_file:
                    data = base64.b64encode(image_file.read())
                    data_str = data.decode("utf-8")

                res = {
                    "src": "data:image/png;base64," + data_str,
                    "width": width,
                    "height": height,
                }
                if self._alt is not None:
                    res["alt"] = self._alt

                return res

            finally:
                matplotlib.pyplot.close(fig)
                os.remove(tmpfile)

        else:
            raise Exception("Unsupported figure type: " + str(type(fig)))


class PlotAsync(Plot, RenderFunctionAsync):
    def __init__(self, fn: UserRenderFunctionAsync, alt: Optional[str]) -> None:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("PlotAsync requires an async function")

        # Init the Plot base class with a placeholder synchronous function so it
        # won't throw an error, then replace it with the async function.
        super().__init__(lambda: None, alt)
        self._fn: UserRenderFunctionAsync = fn

    async def __call__(self) -> object:
        return await self.run()


def plot(alt: Optional[str] = None):
    def wrapper(fn: Union[UserRenderFunction, UserRenderFunctionAsync]) -> Plot:
        if inspect.iscoroutinefunction(fn):
            fn = typing.cast(UserRenderFunctionAsync, fn)
            return PlotAsync(fn, alt)
        else:
            return Plot(fn, alt = alt)

    return wrapper
