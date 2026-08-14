from shiny import reactive
from shiny.express import input, ui

ui.offcanvas(
    ui.p("This panel is declared in the UI."),
    title="Existing panel",
    id="existing_panel",
)
ui.input_action_button("show_existing_btn", "Show existing panel")
ui.input_action_button("show_server_btn", "Show server panel")
ui.input_action_button("show_markdown_btn", "Show markdown content")


@reactive.effect
@reactive.event(input.show_existing_btn)
def _():
    # Reveal a panel already declared in the UI, by its id.
    ui.show_offcanvas("existing_panel")


@reactive.effect
@reactive.event(input.show_server_btn)
def _():
    # Build and show a new, anonymous panel entirely from the server.
    ui.show_offcanvas(
        ui.offcanvas(
            ui.p("This panel was inserted dynamically by the server."),
            title="Server Panel",
            placement="left",
        )
    )


@reactive.effect
@reactive.event(input.show_markdown_btn)
def _():
    # Bare tag content (here, rendered Markdown) is wrapped into a new
    # anonymous panel with default settings.
    ui.show_offcanvas(ui.markdown("""
            ### Markdown content

            This panel's body was written in **Markdown** and wrapped
            into a new anonymous offcanvas by `show_offcanvas()`.
            """))
