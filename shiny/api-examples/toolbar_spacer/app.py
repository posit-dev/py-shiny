from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Spacer Examples"),
    ui.p(
        "The toolbar_spacer() creates a flexible spacer that pushes subsequent toolbar elements to the opposite end."
    ),
    # Example 1: Items on both left and right
    ui.card(
        ui.card_header(
            "My Card",
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
            ui.output_text("output_example1"),
        ),
    ),
    ui.p("Example 2: Multiple items on each side with spacer"),
    # Example 2: Multiple items on each side with spacer
    ui.card(
        ui.card_header(
            "Editor",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="undo", label="Undo", icon=icon_svg("arrow-rotate-left")
                ),
                ui.toolbar_input_button(
                    id="redo", label="Redo", icon=icon_svg("arrow-rotate-right")
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    id="help", label="Help", icon=icon_svg("circle-question")
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
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
        undo_clicks = input.undo()
        redo_clicks = input.redo()
        help_clicks = input.help()
        return f"Undo: {undo_clicks} | Redo: {redo_clicks} | Help: {help_clicks}"


app = App(app_ui, server)
