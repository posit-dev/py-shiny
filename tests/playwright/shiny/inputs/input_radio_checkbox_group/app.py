from htmltools import HTML

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            6,
            ui.input_radio_buttons(
                "radio1",
                "Radio 1:",
                {
                    "a": HTML("<span style='color:red;'>A</span>"),
                    "b": "B",
                    "c": HTML("<span style='color:green;'>C</span>"),
                },
            ),
            ui.output_text_verbatim("radio1_out", placeholder=True),
        ),
        ui.column(
            6,
            ui.input_radio_buttons(
                "radio2",
                "Radio 2 (inline):",
                {
                    "d": HTML("<span style='color:purple;'>D</span>"),
                    "e": "E",
                    "f": HTML("<span style='color:orange;'>F</span>"),
                },
                inline=True,
            ),
            ui.output_text_verbatim("radio2_out", placeholder=True),
        ),
    ),
    ui.row(
        ui.column(
            6,
            ui.input_checkbox_group(
                "check1",
                "Check 1:",
                {
                    "red": ui.span("RED", style="color: #FF0000;"),
                    "green": ui.span("GREEN", style="color: #00AA00;"),
                    "blue": ui.span("BLUE", style="color: #0000AA;"),
                },
            ),
            ui.output_text_verbatim("check1_out", placeholder=True),
        ),
        ui.column(
            6,
            ui.input_checkbox_group(
                "check2",
                "Check 2 (inline):",
                {
                    "magenta": ui.span("MAGENTA", style="color: #FF00AA;"),
                    "orange": ui.span("ORANGE", style="color: #FFAA00;"),
                    "teal": ui.span("TEAL", style="color: #00AAAA;"),
                },
                inline=True,
            ),
            ui.output_text_verbatim("check2_out", placeholder=True),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def radio1_out():
        return input.radio1()

    @render.text
    def radio2_out():
        return input.radio2()

    @render.text
    def check1_out():
        return input.check1()

    @render.text
    def check2_out():
        return input.check2()


app = App(app_ui, server)
