from shiny import App, reactive, render, ui

# For plot rendering
import matplotlib.pyplot as plt
import numpy as np

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


def server(input, output, session):
    @reactive.Calc
    def r():
        return input.N() * 2

    @output
    @render.text
    def txt():
        return f"N*2 is {r()}, session id is {session.id}"

    @output
    @render.plot(alt="A histogram")
    def plot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.N(), density=True)
        return fig

    @output(id="ui")
    @render.ui
    def _():
        return ui.input_slider(
            "N", "This slider is rendered via @render.ui", 0, 100, 20
        )

    @reactive.Effect
    def _():
        btn = input.btn()
        if btn % 2 == 1:
            ui.insert_ui(ui.tags.p("Thanks for clicking!", id="thanks"), "body")
        elif btn > 0:
            ui.remove_ui("#thanks")


app = App(app_ui, server, debug=True)
