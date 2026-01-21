from faicons import icon_svg

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Test App"),
    # Test basic toolbar with buttons
    ui.card(
        ui.card_header(
            "Document Editor",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_save",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                    tooltip="Save your work",
                ),
                ui.toolbar_input_button(
                    "btn_edit",
                    label="Edit",
                    icon=icon_svg("pencil"),
                    show_label=True,
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_delete",
                    label="Delete",
                    icon=icon_svg("trash"),
                    border=True,
                ),
                align="right",
                gap="0.5rem",
            ),
        ),
        ui.card_body(
            ui.output_text("btn_save_value"),
            ui.output_text("btn_edit_value"),
            ui.output_text("btn_delete_value"),
        ),
    ),
    # Test toolbar with select
    ui.card(
        ui.card_header(
            "Filter Controls",
            ui.toolbar(
                ui.toolbar_input_select(
                    "sel_filter",
                    label="Filter",
                    choices=["All", "Active", "Archived"],
                    icon=icon_svg("filter"),
                ),
                ui.toolbar_input_select(
                    "sel_sort",
                    label="Sort",
                    choices={"name": "By Name", "date": "By Date"},
                    selected="date",
                    show_label=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("sel_filter_value"),
            ui.output_text("sel_sort_value"),
        ),
    ),
    # Test updates
    ui.card(
        ui.card_header(
            "Dynamic Controls",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_me",
                    label="Click to Update",
                    icon="👆",
                ),
                ui.toolbar_input_select(
                    "sel_update_me",
                    label="Select",
                    choices=["A", "B", "C"],
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("update_status"),
        ),
    ),
    # Test disabled button
    ui.card(
        ui.card_header(
            "Disabled Button",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_disabled",
                    label="Disabled",
                    icon="🚫",
                    disabled=True,
                ),
                align="right",
            ),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.text
    def btn_save_value():
        return f"Save clicked: {input.btn_save()}"

    @output
    @render.text
    def btn_edit_value():
        return f"Edit clicked: {input.btn_edit()}"

    @output
    @render.text
    def btn_delete_value():
        return f"Delete clicked: {input.btn_delete()}"

    @output
    @render.text
    def sel_filter_value():
        return f"Filter: {input.sel_filter()}"

    @output
    @render.text
    def sel_sort_value():
        return f"Sort: {input.sel_sort()}"

    @output
    @render.text
    def update_status():
        btn_clicks = input.btn_update_me()
        sel_value = input.sel_update_me()
        return f"Button: {btn_clicks}, Select: {sel_value}"

    @reactive.effect
    @reactive.event(input.btn_update_me)
    def _():
        click_count = input.btn_update_me()
        if click_count == 1:
            ui.update_toolbar_input_button(
                "btn_update_me",
                label="Updated!",
                icon="✅",
            )
            ui.update_toolbar_input_select(
                "sel_update_me",
                label="New Label",
                choices=["X", "Y", "Z"],
                selected="Y",
            )
        elif click_count == 2:
            ui.update_toolbar_input_button(
                "btn_update_me",
                disabled=True,
            )


app = App(app_ui, server)
