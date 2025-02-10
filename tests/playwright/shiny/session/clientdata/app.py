import matplotlib.pyplot as plt
import numpy as np

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_slider("obs", "Number of observations:", min=0, max=1000, value=500),
        open="closed",
    ),
    ui.h3("clientData values"),
    ui.output_text_verbatim("clientdatatext"),
    ui.output_plot("myplot"),
    title="Shiny Client Data",
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def clientdatatext():
        cdata = session.clientdata
        return "\n".join([f"{name} = {cdata[name]()}" for name in reversed(dir(cdata))])

    @render.plot
    def myplot():
        plt.figure()
        plt.hist(np.random.normal(size=input.obs()))
        plt.title("This is myplot")


app = App(app_ui, server)
