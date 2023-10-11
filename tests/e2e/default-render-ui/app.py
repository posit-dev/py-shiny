from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(ui.output_ui("dynamic_ui"))


def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def dynamic_ui():
        @render.text
        def txt():
            return "Hello"

        return txt


app = App(app_ui, server)
