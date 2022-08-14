import matplotlib.pyplot as plt
from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("render", "Render", value=True),
    ui.output_plot("mpl"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.plot
    def mpl():
        if input.render():
            plt.hist([1, 1, 2, 3, 5])


app = App(app_ui, server)
