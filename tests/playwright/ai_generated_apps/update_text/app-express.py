from shiny import reactive
from shiny.express import input, render, ui

# Page title
ui.page_opts(fillable=True)

with ui.layout_column_wrap(width=1 / 2):
    # Input text that will be updated
    with ui.card():
        ui.card_header("Text Input Demo")
        ui.input_text(
            "txt",
            "Original Text",
            value="Initial value",
            placeholder="Type something...",
        )

        @render.text
        def current_value():
            return f"Current value: {input.txt()}"

    # Buttons to trigger different update scenarios
    with ui.card():
        ui.card_header("Control Buttons")
        with ui.layout_column_wrap():
            ui.input_action_button(
                "update_all", "Update All Parameters", class_="btn-primary mb-3"
            )
            ui.input_action_button(
                "update_label", "Update Label Only", class_="btn-secondary mb-3"
            )
            ui.input_action_button(
                "update_value", "Update Value Only", class_="btn-success mb-3"
            )
            ui.input_action_button(
                "update_placeholder", "Update Placeholder Only", class_="btn-info mb-3"
            )


# Effects to handle different update scenarios
@reactive.effect
@reactive.event(input.update_all)
def _():
    ui.update_text(
        id="txt",
        label="Updated Label",
        value="Updated Value",
        placeholder="Updated Placeholder",
    )


@reactive.effect
@reactive.event(input.update_label)
def _():
    ui.update_text(id="txt", label=f"Label Updated {input.update_label()} times")


@reactive.effect
@reactive.event(input.update_value)
def _():
    ui.update_text(id="txt", value=f"Value Updated {input.update_value()} times")


@reactive.effect
@reactive.event(input.update_placeholder)
def _():
    ui.update_text(
        id="txt", placeholder=f"Placeholder Updated {input.update_placeholder()} times"
    )
