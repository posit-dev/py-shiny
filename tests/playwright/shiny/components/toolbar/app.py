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
    # Test updates - comprehensive demo of update functionality
    ui.card(
        ui.card_header(
            "Dynamic Controls - Update Demo",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_me",
                    label="Click to Update",
                    icon=icon_svg("hand-pointer"),
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
            ui.tags.ul(
                ui.tags.li(
                    "Click 1: Updates button label, icon, and shows label; updates select choices and label"
                ),
                ui.tags.li(
                    "Click 2: Changes button icon and hides label; updates select choices again"
                ),
                ui.tags.li("Click 3: Disables button"),
            ),
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
                    icon=icon_svg("ban"),
                    disabled=True,
                ),
                align="right",
            ),
        ),
    ),
    # Test toolbar_spacer - basic usage
    ui.card(
        ui.card_header(
            "Spacer Example",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_spacer_left",
                    label="Left Side",
                    icon=icon_svg("align-left"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_spacer_right",
                    label="Right Side",
                    icon=icon_svg("align-right"),
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.output_text("btn_spacer_left_value"),
            ui.output_text("btn_spacer_right_value"),
        ),
    ),
    # Test toolbar_spacer with divider
    ui.card(
        ui.card_header(
            "Spacer + Divider",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_combo_1",
                    label="Undo",
                    icon=icon_svg("rotate-left"),
                ),
                ui.toolbar_input_button(
                    "btn_combo_2",
                    label="Redo",
                    icon=icon_svg("rotate-right"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_combo_3",
                    label="Cut",
                    icon=icon_svg("scissors"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_combo_4",
                    label="Help",
                    icon=icon_svg("circle-question"),
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.output_text("btn_combo_1_value"),
            ui.output_text("btn_combo_2_value"),
            ui.output_text("btn_combo_3_value"),
            ui.output_text("btn_combo_4_value"),
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

    @output
    @render.text
    def btn_spacer_left_value():
        return f"Left Side clicked: {input.btn_spacer_left()}"

    @output
    @render.text
    def btn_spacer_right_value():
        return f"Right Side clicked: {input.btn_spacer_right()}"

    @output
    @render.text
    def btn_combo_1_value():
        return f"Undo clicked: {input.btn_combo_1()}"

    @output
    @render.text
    def btn_combo_2_value():
        return f"Redo clicked: {input.btn_combo_2()}"

    @output
    @render.text
    def btn_combo_3_value():
        return f"Cut clicked: {input.btn_combo_3()}"

    @output
    @render.text
    def btn_combo_4_value():
        return f"Help clicked: {input.btn_combo_4()}"

    @reactive.effect
    @reactive.event(input.btn_update_me)
    def _():
        from faicons import icon_svg

        click_count = input.btn_update_me()
        if click_count == 1:
            # First click: Update button label, icon, and show label
            # Update select choices and label
            ui.update_toolbar_input_button(
                "btn_update_me",
                label="Updated!",
                icon=icon_svg("check"),
                show_label=True,  # Show the label
            )
            ui.update_toolbar_input_select(
                "sel_update_me",
                label="New Options",
                choices=["X", "Y", "Z"],
                selected="Y",
            )
        elif click_count == 2:
            # Second click: Change icon, hide label, update select choices
            ui.update_toolbar_input_button(
                "btn_update_me",
                label="One More!",
                icon=icon_svg("star"),
                show_label=False,  # Hide the label again
            )
            ui.update_toolbar_input_select(
                "sel_update_me",
                label="Final Options",
                choices={"1": "First", "2": "Second", "3": "Third"},
                selected="2",
            )
        elif click_count >= 3:
            # Third click: Disable the button
            ui.update_toolbar_input_button(
                "btn_update_me",
                label="Done!",
                icon=icon_svg("circle-check"),
                show_label=True,
                disabled=True,
            )


app = App(app_ui, server)
