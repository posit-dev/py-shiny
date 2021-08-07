# To run this app:
#   python3 app.py

# Point web browser to:
#   http://localhost:8000/
# Then send JSON messages, e.g.:
#   {"n":1}
#   {"n":4}


from reactives import Reactive, ReactiveVal, ReactiveValues, Observer
from shinyapp import ShinyApp
from shinysession import Outputs
from ui import *

# For plot rendering
import render
import numpy as np
import matplotlib.pyplot as plt



ui = fluid_page(
    "Shiny app demo",
    text_output("txt"),
    slider_input("n")
)

shared_val = ReactiveVal(None)

def server(input: ReactiveValues, output: Outputs):
    print("Running user server function")

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

        # example data
        mu = 100  # mean of distribution
        sigma = 15  # standard deviation of distribution
        x = mu + sigma * np.random.randn(437)

        fig, ax = plt.subplots()

        # the histogram of the data
        ax.hist(x, input["n"], density=True)

        return fig


app = ShinyApp(ui, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(iotype = "tcp")
