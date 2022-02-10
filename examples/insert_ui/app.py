from shiny import *
from shiny.ui import tags

# For plot rendering
import numpy as np
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2("Dynamic UI"),
            ui.output_ui("ui"),
            ui.input_action_button("btn", "Trigger insert/remove ui"),
        ),
        ui.panel_main(
            ui.output_text_verbatim("txt"),
            ui.output_plot("plot"),
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

    @output(name="ui")
    @render_ui()
    def _():
        return ui.input_slider(
            "This slider is rendered via @render_ui()", "N", 0, 100, 20
        )

    @reactive.effect()
    def _():
        btn = input.btn()
        if btn % 2 == 1:
            ui.insert_ui(tags.p("Thanks for clicking!", id="thanks"), "body")
        elif btn > 0:
            ui.remove_ui("#thanks")


app = App(app_ui, server)
