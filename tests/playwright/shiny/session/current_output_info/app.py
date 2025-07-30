from shiny import App, Inputs, Outputs, Session, module, render, ui


@module.ui
def mod_ui():
    return ui.output_text("info2").add_class("shiny-report-theme")


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def info2():
        bg_color = session.clientdata.output_bg_color()
        return f"BG color: {bg_color}"


app_ui = ui.page_fluid(
    ui.input_dark_mode(mode="light", id="dark_mode"),
    ui.output_text("info").add_class("shiny-report-theme"),
    mod_ui("mod1"),
)


def server(input: Inputs, output: Outputs, session: Session):
    mod_server("mod1")

    @render.text
    def info():
        bg_color = session.clientdata.output_bg_color()
        return f"BG color: {bg_color}"


app = App(app_ui, server)
