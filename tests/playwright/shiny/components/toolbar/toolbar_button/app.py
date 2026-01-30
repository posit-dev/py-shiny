from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Input Button Tests"),
    # Test 1: Icon-only button with default tooltip
    ui.card(
        ui.card_header(
            "Test 1: Icon-only with Default Tooltip",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_icon_only",
                    label="Save Document",
                    icon=icon_svg("floppy-disk"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_icon_only"),
        ),
    ),
    # Test 2: Icon and label shown (no tooltip by default)
    ui.card(
        ui.card_header(
            "Test 2: Icon and Label Shown (No Tooltip)",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_with_label",
                    label="Edit",
                    icon=icon_svg("pencil"),
                    show_label=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_with_label"),
        ),
    ),
    # Test 3: Custom tooltip
    ui.card(
        ui.card_header(
            "Test 3: Custom Tooltip",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_custom_tooltip",
                    label="Delete",
                    icon=icon_svg("trash"),
                    tooltip="Remove this item permanently",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_custom_tooltip"),
        ),
    ),
    # Test 4: No tooltip
    ui.card(
        ui.card_header(
            "Test 4: No Tooltip",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_no_tooltip",
                    label="Settings",
                    icon=icon_svg("gear"),
                    tooltip=False,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_no_tooltip"),
        ),
    ),
    # Test 5: Disabled button
    ui.card(
        ui.card_header(
            "Test 5: Disabled Button",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_disabled",
                    label="Undo",
                    icon=icon_svg("rotate-left"),
                    disabled=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_disabled"),
        ),
    ),
    # Test 6: Button with border
    ui.card(
        ui.card_header(
            "Test 6: Button with Border",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_border",
                    label="Upload",
                    icon=icon_svg("upload"),
                    border=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_border"),
        ),
    ),
    # Test 7: Update button - change label
    ui.card(
        ui.card_header(
            "Test 7: Update Label",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_label",
                    label="Initial",
                    show_label=True,
                    icon=icon_svg("circle"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_label"),
        ),
    ),
    # Test 8: Update button - change icon
    ui.card(
        ui.card_header(
            "Test 8: Update Icon",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_icon",
                    label="Toggle",
                    icon=icon_svg("play"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_icon"),
        ),
    ),
    # Test 9: Update button - toggle show_label
    ui.card(
        ui.card_header(
            "Test 9: Toggle Label Visibility",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_toggle_label",
                    label="Download",
                    icon=icon_svg("download"),
                    show_label=False,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_toggle_label"),
        ),
    ),
    # Test 10: Update button - toggle disabled
    ui.card(
        ui.card_header(
            "Test 10: Toggle Disabled State",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_toggle_disabled",
                    label="Submit",
                    icon=icon_svg("paper-plane"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_toggle_disabled"),
        ),
    ),
    # Test 11: Label-only button (no icon) - show_label defaults to True
    ui.card(
        ui.card_header(
            "Test 11: Label Only (No Icon)",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_label_only",
                    label="Click Me",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_label_only"),
        ),
    ),
    # Test 12: Update all properties
    ui.card(
        ui.card_header(
            "Test 12: Update All Properties",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_all",
                    label="Start",
                    icon=icon_svg("play"),
                    show_label=False,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_all"),
        ),
    ),
    # Test 13: Custom data attribute
    ui.card(
        ui.card_header(
            "Test 13: Custom Data Attribute",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_custom_attr",
                    label="Custom",
                    icon=icon_svg("star"),
                    **{"data-testid": "custom-button", "data-category": "featured"},  # type: ignore[reportArgumentType]
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_custom_attr"),
        ),
    ),
    # Test 14: Custom Bootstrap class
    ui.card(
        ui.card_header(
            "Test 14: Custom Bootstrap Class",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_custom_style",
                    label="Danger",
                    icon=icon_svg("triangle-exclamation"),
                    class_="btn-danger",
                    show_label=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_custom_style"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    # Test 1: Icon-only
    @output
    @render.text
    def output_icon_only():
        return f"Icon-only button clicked {input.btn_icon_only()} times"

    # Test 2: With label
    @output
    @render.text
    def output_with_label():
        return f"Button with label clicked {input.btn_with_label()} times"

    # Test 3: Custom tooltip
    @output
    @render.text
    def output_custom_tooltip():
        return f"Custom tooltip button clicked {input.btn_custom_tooltip()} times"

    # Test 4: No tooltip
    @output
    @render.text
    def output_no_tooltip():
        return f"No tooltip button clicked {input.btn_no_tooltip()} times"

    # Test 5: Disabled
    @output
    @render.text
    def output_disabled():
        return f"Disabled button clicked {input.btn_disabled()} times (should stay 0)"

    # Test 6: Border
    @output
    @render.text
    def output_border():
        return f"Border button clicked {input.btn_border()} times"

    # Test 7: Update label
    @output
    @render.text
    def output_update_label():
        return f"Update label button clicked {input.btn_update_label()} times"

    @reactive.effect
    @reactive.event(input.btn_update_label)
    def _():
        count = input.btn_update_label()
        ui.update_toolbar_input_button(
            "btn_update_label",
            label=f"Updated {count}",
        )

    # Test 8: Update icon
    @output
    @render.text
    def output_update_icon():
        return f"Update icon button clicked {input.btn_update_icon()} times"

    @reactive.effect
    @reactive.event(input.btn_update_icon)
    def _():
        count = input.btn_update_icon()
        # Alternate between play and pause icons
        new_icon = icon_svg("pause") if count % 2 == 1 else icon_svg("play")
        ui.update_toolbar_input_button(
            "btn_update_icon",
            icon=new_icon,
        )

    # Test 9: Toggle label visibility
    @output
    @render.text
    def output_toggle_label():
        return f"Toggle label button clicked {input.btn_toggle_label()} times"

    @reactive.effect
    @reactive.event(input.btn_toggle_label)
    def _():
        count = input.btn_toggle_label()
        # Toggle show_label
        ui.update_toolbar_input_button(
            "btn_toggle_label",
            show_label=count % 2 == 1,
        )

    # Test 10: Toggle disabled
    @output
    @render.text
    def output_toggle_disabled():
        return f"Toggle disabled button clicked {input.btn_toggle_disabled()} times"

    @reactive.effect
    @reactive.event(input.btn_toggle_disabled)
    def _():
        count = input.btn_toggle_disabled()
        # Disable after first click
        ui.update_toolbar_input_button(
            "btn_toggle_disabled",
            disabled=count >= 1,
        )

    # Test 11: Label only
    @output
    @render.text
    def output_label_only():
        return f"Label-only button clicked {input.btn_label_only()} times"

    # Test 12: Update all properties
    @output
    @render.text
    def output_update_all():
        return f"Update all button clicked {input.btn_update_all()} times"

    @reactive.effect
    @reactive.event(input.btn_update_all)
    def _():
        count = input.btn_update_all()
        if count == 1:
            # First click: pause, show label
            ui.update_toolbar_input_button(
                "btn_update_all",
                label="Pause",
                icon=icon_svg("pause"),
                show_label=True,
            )
        elif count == 2:
            # Second click: stop, keep label shown
            ui.update_toolbar_input_button(
                "btn_update_all",
                label="Stop",
                icon=icon_svg("stop"),
                show_label=True,
            )
        elif count >= 3:
            # Third click: reset to start
            ui.update_toolbar_input_button(
                "btn_update_all",
                label="Start",
                icon=icon_svg("play"),
                show_label=False,
                disabled=True,
            )

    # Test 13: Custom data attribute
    @output
    @render.text
    def output_custom_attr():
        return f"Custom attr button clicked {input.btn_custom_attr()} times"

    # Test 14: Custom style
    @output
    @render.text
    def output_custom_style():
        return f"Custom style button clicked {input.btn_custom_style()} times"


app = App(app_ui, server)
