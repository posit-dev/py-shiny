from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Input Select Tests"),
    # Test 1: Basic select with list choices
    ui.card(
        ui.card_header(
            "Test 1: Basic Select (List Choices)",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_basic",
                    label="Choose option",
                    choices=["Option 1", "Option 2", "Option 3"],
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_basic"),
        ),
    ),
    # Test 2: Select with dict choices and selected
    ui.card(
        ui.card_header(
            "Test 2: Dict Choices with Selected",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_dict",
                    label="Filter",
                    choices={
                        "all": "All Items",
                        "active": "Active",
                        "archived": "Archived",
                    },
                    selected="active",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_dict"),
        ),
    ),
    # Test 3: Select with icon
    ui.card(
        ui.card_header(
            "Test 3: Select with Icon",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_icon",
                    label="Filter data",
                    choices=["All", "Recent", "Archived"],
                    icon=icon_svg("star"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_icon"),
        ),
    ),
    # Test 4: Select with label shown
    ui.card(
        ui.card_header(
            "Test 4: Select with Label Shown",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_label_shown",
                    label="Sort by",
                    choices=["Name", "Date", "Size"],
                    show_label=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_label_shown"),
        ),
    ),
    # Test 5: Select with custom tooltip
    ui.card(
        ui.card_header(
            "Test 5: Custom Tooltip",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_custom_tooltip",
                    label="View mode",
                    choices=["Grid", "List", "Compact"],
                    tooltip="Change how items are displayed",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_custom_tooltip"),
        ),
    ),
    # Test 6: Select with no tooltip
    ui.card(
        ui.card_header(
            "Test 6: No Tooltip",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_no_tooltip",
                    label="Language",
                    choices=["English", "Spanish", "French"],
                    tooltip=False,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_no_tooltip"),
        ),
    ),
    # Test 7: Grouped choices
    ui.card(
        ui.card_header(
            "Test 7: Grouped Choices",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_grouped",
                    label="Select item",
                    choices={
                        "Group A": {"a1": "Choice A1", "a2": "Choice A2"},
                        "Group B": {"b1": "Choice B1", "b2": "Choice B2"},
                    },
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_grouped"),
        ),
    ),
    # Test 8: Update choices
    ui.card(
        ui.card_header(
            "Test 8: Update Choices",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_choices",
                    label="Update",
                    icon=icon_svg("arrows-rotate"),
                ),
                ui.toolbar_input_select(
                    "select_update_choices",
                    label="Options",
                    choices=["A", "B", "C"],
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_choices"),
        ),
    ),
    # Test 9: Update selected value
    ui.card(
        ui.card_header(
            "Test 9: Update Selected",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_selected",
                    label="Next",
                    icon=icon_svg("forward"),
                ),
                ui.toolbar_input_select(
                    "select_update_selected",
                    label="Current",
                    choices=["First", "Second", "Third"],
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_selected"),
        ),
    ),
    # Test 10: Update label
    ui.card(
        ui.card_header(
            "Test 10: Update Label",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_label",
                    label="Toggle",
                    icon=icon_svg("toggle-on"),
                ),
                ui.toolbar_input_select(
                    "select_update_label",
                    label="Initial Label",
                    choices=["X", "Y", "Z"],
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_label"),
        ),
    ),
    # Test 11: Update show_label
    ui.card(
        ui.card_header(
            "Test 11: Toggle Label Visibility",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_toggle_show_label",
                    label="Toggle",
                    icon=icon_svg("eye"),
                ),
                ui.toolbar_input_select(
                    "select_toggle_show_label",
                    label="Visibility",
                    choices=["Option 1", "Option 2"],
                    show_label=False,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_toggle_show_label"),
        ),
    ),
    # Test 12: Update icon
    ui.card(
        ui.card_header(
            "Test 12: Update Icon",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_update_icon",
                    label="Change",
                    icon=icon_svg("wand-magic-sparkles"),
                ),
                ui.toolbar_input_select(
                    "select_update_icon",
                    label="Mode",
                    choices=["Light", "Dark"],
                    icon=icon_svg("sun"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_icon"),
        ),
    ),
    # Test 13: Update all properties
    ui.card(
        ui.card_header(
            "Test 13: Update All Properties",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_update_all",
                    label="Status",
                    choices=["Active", "Inactive"],
                    selected="Inactive",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_update_all"),
        ),
    ),
    # Test 14: Icon and label shown
    ui.card(
        ui.card_header(
            "Test 14: Icon and Label Shown",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_icon_label",
                    label="Priority",
                    choices={"high": "High", "medium": "Medium", "low": "Low"},
                    icon=icon_svg("flag"),
                    show_label=True,
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_icon_label"),
        ),
    ),
    # Test 15: Custom attributes
    ui.card(
        ui.card_header(
            "Test 15: Custom Attributes",
            ui.toolbar(
                ui.toolbar_input_select(
                    "select_custom_attr",
                    label="Category",
                    choices=["Tech", "Science", "Arts"],
                    **{
                        "data-testid": "category-select",
                        "style": "background-color: #f9b928;",
                    },  # type: ignore[reportArgumentType]
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_custom_attr"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    # Test 1: Basic select
    @output
    @render.text
    def output_basic():
        return f"Basic select value: {input.select_basic()}"

    # Test 2: Dict choices
    @output
    @render.text
    def output_dict():
        return f"Dict select value: {input.select_dict()}"

    # Test 3: Icon
    @output
    @render.text
    def output_icon():
        return f"Icon select value: {input.select_icon()}"

    # Test 4: Label shown
    @output
    @render.text
    def output_label_shown():
        return f"Label shown value: {input.select_label_shown()}"

    # Test 5: Custom tooltip
    @output
    @render.text
    def output_custom_tooltip():
        return f"Custom tooltip value: {input.select_custom_tooltip()}"

    # Test 6: No tooltip
    @output
    @render.text
    def output_no_tooltip():
        return f"No tooltip value: {input.select_no_tooltip()}"

    # Test 7: Grouped
    @output
    @render.text
    def output_grouped():
        return f"Grouped select value: {input.select_grouped()}"

    # Test 8: Update choices
    @output
    @render.text
    def output_update_choices():
        return f"Update choices value: {input.select_update_choices()}"

    @reactive.effect
    @reactive.event(input.btn_update_choices)
    def _():
        count = input.btn_update_choices()
        if count % 2 == 1:
            ui.update_toolbar_input_select(
                "select_update_choices",
                choices=["X", "Y", "Z"],
            )
        else:
            ui.update_toolbar_input_select(
                "select_update_choices",
                choices=["A", "B", "C"],
                selected="B",
            )

    # Test 9: Update selected
    @output
    @render.text
    def output_update_selected():
        return f"Update selected value: {input.select_update_selected()}"

    @reactive.effect
    @reactive.event(input.btn_update_selected)
    def _():
        current = input.select_update_selected()
        if current == "First":
            ui.update_toolbar_input_select("select_update_selected", selected="Second")
        elif current == "Second":
            ui.update_toolbar_input_select("select_update_selected", selected="Third")
        else:
            ui.update_toolbar_input_select("select_update_selected", selected="First")

    # Test 10: Update label
    @output
    @render.text
    def output_update_label():
        return f"Update label value: {input.select_update_label()}"

    @reactive.effect
    @reactive.event(input.btn_update_label)
    def _():
        count = input.btn_update_label()
        ui.update_toolbar_input_select(
            "select_update_label",
            show_label=True,
            label=f"Updated {count}",
        )

    # Test 11: Toggle show_label
    @output
    @render.text
    def output_toggle_show_label():
        return f"Toggle show_label value: {input.select_toggle_show_label()}"

    @reactive.effect
    @reactive.event(input.btn_toggle_show_label)
    def _():
        count = input.btn_toggle_show_label()
        ui.update_toolbar_input_select(
            "select_toggle_show_label",
            show_label=count % 2 == 1,
        )

    # Test 12: Update icon
    @output
    @render.text
    def output_update_icon():
        return f"Update icon value: {input.select_update_icon()}"

    @reactive.effect
    @reactive.event(input.btn_update_icon)
    def _():
        count = input.btn_update_icon()
        new_icon = icon_svg("moon") if count % 2 == 1 else icon_svg("sun")
        ui.update_toolbar_input_select(
            "select_update_icon",
            icon=new_icon,
        )

    # Test 13: Update all
    @output
    @render.text
    def output_update_all():
        return f"Update all value: {input.select_update_all()}"

    @reactive.effect
    @reactive.event(input.select_update_all)
    def _():
        current = input.select_update_all()
        if current == "Active":
            ui.update_toolbar_input_select(
                "select_update_all",
                label="New Status",
                choices=["Online", "Offline", "Busy"],
                selected="Online",
                icon=icon_svg("circle"),
                show_label=True,
            )

    # Test 14: Icon and label
    @output
    @render.text
    def output_icon_label():
        return f"Icon and label value: {input.select_icon_label()}"

    # Test 15: Custom attributes
    @output
    @render.text
    def output_custom_attr():
        return f"Custom attr value: {input.select_custom_attr()}"


app = App(app_ui, server)
