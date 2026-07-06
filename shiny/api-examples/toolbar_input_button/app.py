from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Input Button Examples"),
    ui.p(
        "Examples showing different ways to configure toolbar_input_button: label-only, icon-only, and label with icon and custom tooltip."
    ),
    ui.card(
        ui.card_header(
            "Label-only Button",
            ui.toolbar(
                ui.toolbar_input_button(id="save", label="Save"),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_example1"),
        ),
    ),
    ui.card(
        ui.card_header(
            "Icon-only Button",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="edit", label="Edit", icon=icon_svg("pencil")
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_example2"),
        ),
    ),
    ui.card(
        ui.card_header(
            "Label and Icon Button",
            ui.toolbar(
                ui.toolbar_input_button(
                    id="edit_with_label",
                    label="Edit",
                    show_label=True,
                    icon=icon_svg("pencil"),
                    tooltip="Edit Document",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_example3"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def output_example1():
        save_clicks = input.save()
        return f"Save clicks: {save_clicks}"

    @output
    @render.text
    def output_example2():
        edit_clicks = input.edit()
        return f"Edit clicks: {edit_clicks}"

    @output
    @render.text
    def output_example3():
        edit_clicks = input.edit_with_label()
        return f"Edit clicks: {edit_clicks}"


app = App(app_ui, server)
