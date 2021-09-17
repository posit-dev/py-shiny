# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

# Add parent directory to path, so we can find the prism module.
# (This is just a temporary fix)
import os
import sys

# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)

from shiny import *
from shiny.fileupload import FileInfo

# For plot rendering
import shiny.render as render
import numpy as np
import matplotlib.pyplot as plt

# A ReactiveVal which is shared across all sessions.
shared_val = ReactiveVal(None)

def server(input: ReactiveValues, output: Outputs):
    @reactive()
    def r():
        if input["n"] is None:
            return
        return input["n"] * 2

    @output.set("txt")
    async def _():
        val = r()
        return f"n*2 is {val}, session id is {get_current_session().id}"

    # This observer watches n, and changes shared_val, which is shared across
    # all running sessions.
    @observer()
    def _():
        if input["n"] is None:
            return
        shared_val( input["n"] * 10 )

    # Print the value of shared_val(). Changing it in one session should cause
    # this to run in all sessions.
    @output.set("shared_txt")
    def _():
        return f"shared_val() is {shared_val()}"


    @output.set("plot")
    @render.plot(alt = "A histogram")
    def _():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input["n"], density=True)
        return fig

    @output.set("file_content")
    def _():
        file_infos: list[FileInfo] = input["file1"]
        if not file_infos:
            return

        out_str = ""
        for file_info in file_infos:
            out_str += "====== " + file_info["name"] + " ======\n"
            with open(file_info["datapath"], "r") as f:
                out_str += f.read()

        return out_str


ui_path = os.path.join(os.path.dirname(__file__), "www")

app = ShinyApp(ui_path, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
