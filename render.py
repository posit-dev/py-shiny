import os
import tempfile
import base64
import matplotlib.figure
from typing import TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from shinysession import ShinySession

class RenderFunction:
    def __init__(self, fn: Callable[[], Any]) -> None:
        raise NotImplementedError

    def __call__(self) -> Any:
        raise NotImplementedError

    def set_metadata(self, session: 'ShinySession', name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session = session
        self._name = name



class Plot(RenderFunction):
    _ppi: float = 96

    def __init__(self, fn: Callable[[], Any]) -> None:
        self._fn = fn

    def __call__(self) -> Any:

        # Reactively read some information about the plot.
        pixelratio = self._session.input[f".clientdata_pixelratio"]
        width = self._session.input[f".clientdata_output_{self._name}_width"]
        height = self._session.input[f".clientdata_output_{self._name}_height"]

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

                return {
                    "src": "data:image/png;base64," + data_str,
                    "width": width,
                    "height": height
                }

            finally:
                os.remove(tmpfile)

        else:
            raise Exception("Unsupported figure type: " + str(type(fig)))
