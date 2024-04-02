from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar("Sidebar content", id="sidebar"),
    ui.input_action_button("open_sidebar", label="Open sidebar", class_="me-3"),
    ui.input_action_button("close_sidebar", label="Close sidebar", class_="me-3"),
    ui.br(),
    ui.br(),
    ui.output_text_verbatim("state"),
    fillable=False,
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.open_sidebar)
    def _():
        ui.update_sidebar("sidebar", show=True)

    @reactive.effect
    @reactive.event(input.close_sidebar)
    def _():
        ui.update_sidebar("sidebar", show=False)

    @render.text
    def state():
        return f"input.sidebar(): {input.sidebar()}"


app = App(app_ui, server=server)
