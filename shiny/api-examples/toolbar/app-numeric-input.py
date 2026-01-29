from faicons import icon_svg

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar in Numeric Input Label"),
    ui.p(
        "This example shows how to add preset value buttons to a numeric input using a toolbar in the label."
    ),
    ui.card(
        ui.card_header("Quantity Input with Presets"),
        ui.card_body(
            ui.input_numeric(
                "quantity",
                label=ui.toolbar(
                    ui.toolbar_spacer(),
                    ui.toolbar_input_button(
                        "btn_preset_10",
                        label="10",
                        show_label=True,
                        tooltip="Set to 10",
                    ),
                    ui.toolbar_input_button(
                        "btn_preset_50",
                        label="50",
                        show_label=True,
                        tooltip="Set to 50",
                    ),
                    ui.toolbar_input_button(
                        "btn_preset_100",
                        label="100",
                        show_label=True,
                        tooltip="Set to 100",
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "btn_reset",
                        label="Reset",
                        icon=icon_svg("rotate-left"),
                        tooltip="Reset to 1",
                    ),
                    align="right",
                ),
                value=1,
                min=1,
                max=1000,
            ),
            ui.output_text("quantity_status"),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.text
    def quantity_status():
        quantity = input.quantity()
        return f"Current quantity: {quantity}"

    @reactive.effect
    @reactive.event(input.btn_preset_10)
    def _():
        ui.update_numeric("quantity", value=10)

    @reactive.effect
    @reactive.event(input.btn_preset_50)
    def _():
        ui.update_numeric("quantity", value=50)

    @reactive.effect
    @reactive.event(input.btn_preset_100)
    def _():
        ui.update_numeric("quantity", value=100)

    @reactive.effect
    @reactive.event(input.btn_reset)
    def _():
        ui.update_numeric("quantity", value=1)


app = App(app_ui, server)
