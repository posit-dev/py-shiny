from typing import Callable, Any

import matplotlib.figure
import base64

def plot(fn: Callable[[], Any]) -> Callable[[], Any]:

    def wrapper() -> Any:
        fig = fn()
        if (isinstance(fig, matplotlib.figure.Figure)):
            tempfilename = "shiny_render_plot.png"
            fig.savefig(tempfilename)

            with open(tempfilename, "rb") as image_file:
                data = base64.b64encode(image_file.read())
                data_str = data.decode("utf-8")

            return { "src": "data:image/png;base64," + data_str }

        else:
            raise Exception("Unsupported figure type: " + str(type(fig)))


    return wrapper


def render_text(fn):
    def wrapper():
        print("render_text")
        fn()
        print("done")
    return wrapper