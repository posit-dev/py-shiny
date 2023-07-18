from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_text("txt", "Enter the text to display below:", "delete me"),
    ui.row(
        ui.column(6, ui.code("ui.output_text()"), ui.output_text("text")),
        ui.column(
            6,
            ui.code("ui.output_text_verbatim(placeholder=True)"),
            ui.output_text_verbatim("verb", placeholder=True),
        ),
    ),
    ui.row(
        ui.column(6),
        ui.column(
            6,
            ui.code("ui.output_text_verbatim(placeholder=False)"),
            ui.output_text_verbatim("verb_no_placeholder", placeholder=False),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    def text():
        return input.txt()

    @output
    @render.text
    def verb():
        return input.txt()

    @output
    @render.text
    def verb_no_placeholder():
        return input.txt()


app = App(app_ui, server)
