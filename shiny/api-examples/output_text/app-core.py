from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_text("txt", "Enter the text to display below:", "delete me"),
    ui.row(
        ui.column(6, ui.code("ui.output_text()"), ui.output_text("text")),
        ui.column(
            6,
            ui.code("ui.output_code(placeholder=True)"),
            ui.output_code("verb", placeholder=True),
        ),
    ),
    ui.row(
        ui.column(6),
        ui.column(
            6,
            ui.code("ui.output_code(placeholder=False)"),
            ui.output_code("verb_no_placeholder", placeholder=False),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def text():
        return input.txt()

    @render.code
    def verb():
        return input.txt()

    @render.code
    def verb_no_placeholder():
        return input.txt()


app = App(app_ui, server)
