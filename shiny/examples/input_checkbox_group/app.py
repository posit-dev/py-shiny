from shiny import *
from fontawesome import icon_svg as icon

app_ui = ui.page_fluid(
    ui.input_checkbox_group(
        "icons",
        "Choose icons:",
        {
            "calendar": icon("calendar"),
            "bed": icon("bed"),
            "cog": icon("cog"),
            "bug": icon("bug"),
        },
    ),
    ui.output_ui("val"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def val():
        return "You chose " + str(input.icons())


app = App(app_ui, server)
