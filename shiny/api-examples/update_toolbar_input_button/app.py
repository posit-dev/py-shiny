from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Update Toolbar Input Button Examples"),
    ui.p(
        "These examples demonstrate updating a toolbar button's label and icon on click."
    ),
    ui.card(
        ui.card_header(
            "Update Label",
            ui.toolbar(ui.toolbar_input_button("btn", label="Click me"), align="right"),
        ),
        ui.card_body(
            ui.output_text_verbatim("count"),
        ),
    ),
    ui.card(
        ui.card_header(
            "Update Icon",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_icon", label="Save", icon=icon_svg("floppy-disk")
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text_verbatim("count_icon"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def count():
        return f"Button clicked {input.btn()} times"

    @reactive.effect
    @reactive.event(input.btn)
    def _():
        if input.btn() == 1:
            ui.update_toolbar_input_button("btn", label="Clicked!")

    @output
    @render.text
    def count_icon():
        return f"Button clicked {input.btn_icon()} times"

    @reactive.effect
    @reactive.event(input.btn_icon)
    def _():
        if input.btn_icon() == 1:
            ui.update_toolbar_input_button(
                "btn_icon", icon=icon_svg("circle-check"), label="Saved"
            )


app = App(app_ui, server)
