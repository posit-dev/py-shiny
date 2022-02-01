from shiny import *
from fontawesome import icon_svg as icon
from htmltools import HTML

app_ui = ui.page_fluid(
    ui.input_radio_buttons(
        "rb",
        "Choose one:",
        {
            "icon": icon("calendar"),
            "html": HTML("<span style='color:red;'>Red Text</span>"),
            "text": "Normal text",
        },
    ),
    ui.output_ui("val"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_ui()
    def val():
        return "You chose " + input.rb()


app = App(app_ui, server)
