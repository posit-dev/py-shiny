# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

import shiny.ui_toolkit as st
from shiny import *
from htmltools import *

# For plot rendering
import numpy as np
import matplotlib.pyplot as plt

ui = st.page_fluid(
    st.layout_sidebar(
        st.panel_sidebar(
            st.h2("Dynamic UI"),
            st.output_ui("ui"),
            st.input_action_button("btn", "Trigger insert/remove ui"),
        ),
        st.panel_main(
            st.output_text_verbatim("txt"),
            st.output_plot("plot"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc()
    def r():
        if input.n() is None:
            return
        return input.n() * 2

    @output()
    @render_text()
    async def txt():
        val = r()
        return f"n*2 is {val}, session id is {session.id}"

    @output()
    @render_plot(alt="A histogram")
    def plot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig

    @output()
    @render_ui()
    def ui():
        return st.input_slider(
            "This slider is rendered via @render_ui()", "N", 0, 100, 20
        )

    @reactive.effect()
    def _():
        btn = input.btn()
        if btn % 2 == 1:
            ui_insert(tags.p("Thanks for clicking!", id="thanks"), "body")
        elif btn > 0:
            ui_remove("#thanks")


app = App(ui, server)
