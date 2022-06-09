from shiny import *
import numpy as np
import matplotlib.pyplot as plt

app_ui = ui.page_fluid(
    ui.input_slider("n", "Number of observations", min=0, max=1000, value=500),
    ui.input_action_link("go", "Go!"),
    ui.output_plot("plt"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output(name="plt")
    @render.plot(alt="A histogram")
    # bind_event() to invalidate the plot when the button is pressed
    # but not when the slider is changed
    @event(lambda: input.go, ignore_none=False)
    def _():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(input.n())
        fig, ax = plt.subplots()
        ax.hist(x, bins=30, density=True)
        return fig


app = App(app_ui, server)
