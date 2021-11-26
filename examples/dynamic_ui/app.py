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

# For plot rendering
import numpy as np
import matplotlib.pyplot as plt

ui = page_fluid(
    layout_sidebar(
        panel_sidebar(h2("Dynamic UI"), output_ui("ui")),
        panel_main(
            output_text_verbatim("txt"),
            output_plot("plot"),
        ),
    ),
)


def server(session: ShinySession):
    @reactive()
    def r():
        if session.input["n"] is None:
            return
        return session.input["n"] * 2

    @session.output("txt")
    async def _():
        val = r()
        return f"n*2 is {val}, session id is {get_current_session().id}"

    @session.output("plot")
    @render_plot(alt="A histogram")
    def _():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, session.input["n"], density=True)
        return fig

    @session.output("ui")
    @render_ui()
    def _():
        return input_slider("n", "N", 0, 100, 20)


app = ShinyApp(ui, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
