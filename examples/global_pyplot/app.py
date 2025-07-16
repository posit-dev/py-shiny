import matplotlib.pyplot as plt

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_checkbox("render", "Render", value=True),
    ui.panel_conditional(
        "input.render",
        ui.tags.h5("A plot should appear immediately below this text."),
    ),
    ui.output_plot("mpl"),
    ui.tags.hr(),
    ui.panel_conditional(
        "input.render",
        ui.tags.h5("An error message should appear immediately below this text."),
    ),
    ui.output_plot("mpl_bad"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.plot
    def mpl():
        if input.render():
            plt.hist([1, 1, 2, 3, 5])

    @render.plot
    async def mpl_bad():
        if input.render():
            plt.hist([1, 1, 2, 3, 5])


app = App(app_ui, server)
