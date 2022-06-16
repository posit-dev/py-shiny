from shiny import *
import numpy as np
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of observations", min=0, max=1000, value=500),
    ui.input_action_button("go", "Go!", class_="btn-success"),
    ui.output_plot("plot"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot(alt="A histogram")
    def plot():
        # Take a reactive dependency on the action button...
        input.go()

        # ...but don't take a reactive dependency on the slider
        with reactive.isolate():
            np.random.seed(19680801)
            x = 100 + 15 * np.random.randn(input.n())

        fig, ax = plt.subplots()
        ax.hist(x, bins=30, density=True)
        return fig


app = App(app_ui, server)
