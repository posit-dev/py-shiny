"""An app the `local_server` fixture only reaches via an indirect parametrization.

It lives in another directory so the indirect param exercises a relative path,
not just another file name.
"""

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fixed(ui.output_text("tripled"))


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def tripled():
        return str(input.n() * 3)


app = App(app_ui, server)
