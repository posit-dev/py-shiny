from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Spacer Examples"),
    ui.p(
        "The toolbar_spacer() creates a flexible spacer that pushes subsequent toolbar elements to the opposite end."
    ),
    ui.card(
        ui.card_header(
            ui.toolbar(
                ui.toolbar_input_button(id="save", label="Save"),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    id="settings", label="Settings", icon=icon_svg("gear")
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.p("The above header is a toolbar with two buttons split by a spacer"),
        ),
    ),
    ui.card(
        ui.card_header("Toolbar buttons in numeric input label with spacer"),
        ui.card_body(
            ui.input_numeric(
                "quantity",
                label=ui.toolbar(
                    ui.toolbar_spacer(),
                    ui.toolbar_input_button(
                        id="preset_10",
                        label="10",
                        show_label=True,
                        tooltip="Set to 10",
                    ),
                    ui.toolbar_input_button(
                        id="preset_50",
                        label="50",
                        show_label=True,
                        tooltip="Set to 50",
                    ),
                    ui.toolbar_input_button(
                        id="preset_100",
                        label="100",
                        show_label=True,
                        tooltip="Set to 100",
                    ),
                    align="left",
                ),
                value=1,
                min=1,
                max=1000,
            ),
            ui.output_text("output_example2"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def output_example1():
        save_clicks = input.save()
        settings_clicks = input.settings()
        return f"Save: {save_clicks} clicks | Settings: {settings_clicks} clicks"

    @output
    @render.text
    def output_example2():
        quantity = input.quantity()
        return f"Current quantity: {quantity}"

    @reactive.effect
    @reactive.event(input.preset_10)
    def _():
        ui.update_numeric("quantity", value=10)

    @reactive.effect
    @reactive.event(input.preset_50)
    def _():
        ui.update_numeric("quantity", value=50)

    @reactive.effect
    @reactive.event(input.preset_100)
    def _():
        ui.update_numeric("quantity", value=100)


app = App(app_ui, server)
