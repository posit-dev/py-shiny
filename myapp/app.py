# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

# Add parent directory to path, so we can find the prism module.
# (This is just a temporary fix)
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from reactives import Reactive, ReactiveVal, ReactiveValues, Observer
from shinyapp import ShinyApp
from shinysession import Outputs

# For plot rendering
import render
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
    def _():
        return f"n*2 is {r()}"

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
    @render.plot
    def _():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input["n"], density=True)
        return fig


ui_path = os.path.join(os.path.dirname(__file__), "www")

app = ShinyApp(ui_path, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
