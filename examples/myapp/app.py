# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

import matplotlib.pyplot as plt

# For plot rendering
import numpy as np

import shiny.ui_toolkit as st
import shiny
from shiny import Session, Inputs, Outputs, reactive
from shiny.fileupload import FileInfo

ui = st.page_fluid(
    st.layout_sidebar(
        st.panel_sidebar(
            st.input_slider("n", "N", 0, 100, 20),
            st.input_file("file1", "Choose file", multiple=True),
        ),
        st.panel_main(
            st.output_text_verbatim("txt"),
            st.output_text_verbatim("shared_txt"),
            st.output_plot("plot"),
            st.output_text_verbatim("file_content"),
        ),
    ),
)

# A ReactiveVal which is shared across all sessions.
shared_val = reactive.Value(None)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.reactive()
    def r():
        if input.n() is None:
            return
        return input.n() * 2

    @output()
    @shiny.render_text()
    async def txt():
        val = r()
        return f"n*2 is {val}, session id is {shiny.session.get_current_session().id}"

    # This observer watches n, and changes shared_val, which is shared across
    # all running sessions.
    @reactive.observe()
    def _():
        if input.n() is None:
            return
        shared_val.set(input["n"]() * 10)

    # Print the value of shared_val(). Changing it in one session should cause
    # this to run in all sessions.
    @output()
    @shiny.render_text()
    def shared_txt():
        return f"shared_val() is {shared_val()}"

    @output()
    @shiny.render_plot(alt="A histogram")
    def plot() -> object:
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.n(), density=True)
        return fig

    @output()
    @shiny.render_text()
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


app = shiny.App(ui, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
