import os
import tempfile
import base64
import matplotlib.figure
import matplotlib.pyplot
from typing import TYPE_CHECKING, Callable, Optional
import typing
if TYPE_CHECKING:
    from .shinysession import ShinySession

class RenderFunction:
    def __init__(self, fn: Callable[[], object]) -> None:
        raise NotImplementedError

    def __call__(self) -> object:
        raise NotImplementedError

    def set_metadata(self, session: 'ShinySession', name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session = session
        self._name = name



class Plot(RenderFunction):
    _ppi: float = 96

    def __init__(self, fn: Callable[[], object], alt: Optional[str] = None) -> None:
        self._fn = fn
        self._alt: Optional[str] = alt

    def __call__(self) -> object:

        # Reactively read some information about the plot.
        pixelratio: float = typing.cast(float, self._session.input[f".clientdata_pixelratio"])
        width: float = typing.cast(float, self._session.input[f".clientdata_output_{self._name}_width"])
        height: float = typing.cast(float, self._session.input[f".clientdata_output_{self._name}_height"])

        fig = self._fn()

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


def plot(alt: Optional[str] = None):
    def wrapper(fn: Callable[[], object]) -> Plot:
        return Plot(fn, alt = alt)

    return wrapper
