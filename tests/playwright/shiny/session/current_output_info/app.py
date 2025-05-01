from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_dark_mode(mode="light", id="dark_mode"),
    ui.output_text("text1"),
    ui.output_text("text2"),
    ui.output_text("info").add_class("shiny-report-theme"),
)


def server(input: Inputs, output: Outputs, session: Session):

    @render.text
    def info():
        bg_color = session.clientdata.output_bg_color()
        return f"BG color: {bg_color}"


app = App(app_ui, server)
