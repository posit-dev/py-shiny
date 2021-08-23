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

from shiny.reactives import Reactive, ReactiveVal, ReactiveValues, Observer
from shiny.shinyapp import ShinyApp
from shiny.shinysession import Outputs, get_current_session

# For plot rendering
import shiny.render as render
import numpy as np
import matplotlib.pyplot as plt

# A ReactiveVal which is shared across all sessions.
shared_val = ReactiveVal(None)

def server(input: ReactiveValues, output: Outputs):
    @Reactive
    def r():
        if input["n"] is None:
            return
        return input["n"] * 2

    @output.set("txt")
    async def _():
        val = r()
        return f"n*2 is {val}, session id is {get_current_session().id}\n" + \
               f"input file1 is {input['file1']}"

    # This observer watches n, and changes shared_val, which is shared across
    # all running sessions.
    @Observer
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
        filename =input["file1"]
        if filename is None:
            return
        with open(filename, "r") as f:
            return f.read()


ui_path = os.path.join(os.path.dirname(__file__), "www")

app = ShinyApp(ui_path, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
