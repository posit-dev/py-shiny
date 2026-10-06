from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 1, 10, 3),
    ui.output_text("out"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def doubled() -> int:
        return input.n() * 2

    @render.text
    def out():
        return str(doubled())


app = App(app_ui, server)
