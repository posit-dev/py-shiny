from shiny import *
from shiny.types import FileInfo
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("n", "N", min=0, max=100, value=20),
            ui.input_file("file1", "Choose file", multiple=True),
        ),
        ui.panel_main(
            ui.output_text_verbatim("txt"),
            ui.output_text_verbatim("shared_txt"),
            ui.output_plot("plot"),
            ui.output_text_verbatim("file_content"),
        ),
    ),
)

# A ReactiveVal which is shared across all sessions.
shared_val = reactive.Value(None)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc()
    def r():
        if input.n() is None:
            return
        return input.n() * 2

    @output()
    @render.text()
    async def txt():
        val = r()
        return f"n*2 is {val}, session id is {session.id}"

    # This observer watches n, and changes shared_val, which is shared across
    # all running sessions.
    @reactive.Effect()
    def _():
        if input.n() is None:
            return
        shared_val.set(input.n() * 10)

    # Print the value of shared_val(). Changing it in one session should cause
    # this to run in all sessions.
    @output()
    @render.text()
    def shared_txt():
        return f"shared_val() is {shared_val()}"

    @output()
    @render.plot(alt="A histogram")
    def plot() -> object:
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig

    @output()
    @render.text()
    def file_content():
        file_infos: list[FileInfo] = input.file1()
        if not file_infos:
            return ""

        out_str = ""
        for file_info in file_infos:
            out_str += "====== " + file_info["name"] + " ======\n"
            with open(file_info["datapath"], "r") as f:
                out_str += f.read()

        return out_str


app = App(app_ui, server)
