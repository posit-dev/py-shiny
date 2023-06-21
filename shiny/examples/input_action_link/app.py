import matplotlib.pyplot as plt
import numpy as np

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of observations", min=0, max=1000, value=500),
    ui.input_action_link("go", "Go!"),
    ui.output_plot("plot"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot(alt="A histogram")
    # reactive.event() to invalidate the plot when the button is pressed but not when
    # the slider is changed
    @reactive.event(input.go, ignore_none=False)
    def plot():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(input.n())
        fig, ax = plt.subplots()
        ax.hist(x, bins=30, density=True)
        return fig


app = App(app_ui, server)
