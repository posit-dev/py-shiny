from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_radio_buttons(
        "rb",
        "Choose one:",
        {
            "html": ui.HTML("<span style='color:red;'>Red Text</span>"),
            "text": "Normal text",
        },
    ),
    ui.output_ui("val"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def val():
        return "You chose " + input.rb()


app = App(app_ui, server)
