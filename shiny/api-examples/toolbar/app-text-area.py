from faicons import icon_svg

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar in Text Area Label"),
    ui.p(
        "This example shows how to add formatting controls to a text area using a toolbar in the label."
    ),
    ui.card(
        ui.card_header("Notes with Formatting Controls"),
        ui.card_body(
            ui.input_text_area(
                "notes",
                label=ui.toolbar(
                    ui.toolbar_input_button(
                        "btn_bold",
                        label="Bold",
                        icon=icon_svg("bold"),
                        tooltip="Make text bold",
                    ),
                    ui.toolbar_input_button(
                        "btn_italic",
                        label="Italic",
                        icon=icon_svg("italic"),
                        tooltip="Make text italic",
                    ),
                    ui.toolbar_input_button(
                        "btn_link",
                        label="Link",
                        icon=icon_svg("link"),
                        tooltip="Insert link",
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_select(
                        "text_size",
                        label="Text Size",
                        choices={
                            "small": "Small",
                            "normal": "Normal",
                            "large": "Large",
                        },
                        selected="normal",
                        show_label=False,
                    ),
                    ui.toolbar_spacer(),
                    ui.toolbar_input_button(
                        "btn_clear",
                        label="Clear",
                        icon=icon_svg("eraser"),
                        tooltip="Clear all text",
                        border=True,
                    ),
                    align="right",
                ),
                placeholder="Type your notes here...",
                rows=6,
            ),
            ui.output_text("notes_status"),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.text
    def notes_status():
        text_size = input.text_size()
        clicks_bold = input.btn_bold()
        clicks_italic = input.btn_italic()
        clicks_link = input.btn_link()
        return f"Text Size: {text_size} | Bold: {clicks_bold}, Italic: {clicks_italic}, Link: {clicks_link}"

    @reactive.effect
    @reactive.event(input.btn_clear)
    def _():
        ui.update_text_area("notes", value="")


app = App(app_ui, server)
