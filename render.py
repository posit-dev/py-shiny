from typing import Callable, Any
import os
import tempfile
import base64
import matplotlib.figure

class Plot:
    def __init__(self, fn: Callable[[], Any]) -> None:
        self._fn = fn

    def __call__(self) -> Any:
        fig = self._fn()

        if (isinstance(fig, matplotlib.figure.Figure)):
            tmpfile = tempfile.mkstemp(suffix = ".png")[1]

            try:
                fig.savefig(tmpfile)

                with open(tmpfile, "rb") as image_file:
                    data = base64.b64encode(image_file.read())
                    data_str = data.decode("utf-8")

                return { "src": "data:image/png;base64," + data_str }

            finally:
                os.remove(tmpfile)

        else:
            raise Exception("Unsupported figure type: " + str(type(fig)))

