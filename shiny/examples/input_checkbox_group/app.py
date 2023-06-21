from shiny import App, Inputs, Outputs, Session, render, req, ui

app_ui = ui.page_fluid(
    ui.input_checkbox_group(
        "colors",
        "Choose color(s):",
        {
            "red": ui.span("Red", style="color: #FF0000;"),
            "green": ui.span("Green", style="color: #00AA00;"),
            "blue": ui.span("Blue", style="color: #0000AA;"),
        },
    ),
    ui.output_ui("val"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def val():
        req(input.colors())
        return "You chose " + ", ".join(input.colors())


app = App(app_ui, server)
