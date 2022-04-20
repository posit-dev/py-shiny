from shiny import *

app_ui = ui.page_fluid(
    ui.h3("HTTP request headers"),
    ui.output_text_verbatim("txt", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_text()
    def txt():
        s = ""
        for key, value in session.http_conn.headers.items():
            s += f"{key}: {value}\n"

        return s


app = App(app_ui, server)
