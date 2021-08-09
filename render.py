from typing import Callable, Any
import os
import tempfile
import base64
import matplotlib.figure

from shinysession import ShinySession

class Plot:
    def __init__(self, fn: Callable[[], Any]) -> None:
        self._fn = fn

    def __call__(self, session: ShinySession, name: str) -> Any:

        pixelratio = session.input[f".clientdata_pixelratio"]
        width  = session.input[f".clientdata_output_{name}_width"]
        height = session.input[f".clientdata_output_{name}_height"]

        pixelratio = 2
        fig = self._fn()
        fig.set_dpi(72 * pixelratio)
        fig.set_size_inches(width / 72, height  / 72)

        if (isinstance(fig, matplotlib.figure.Figure)):
            tmpfile = tempfile.mkstemp(suffix = ".png")[1]

            try:
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

