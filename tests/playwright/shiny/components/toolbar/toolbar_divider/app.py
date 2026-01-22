from faicons import icon_svg

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Divider and Spacer Test App"),
    # Test 1: Basic divider with default settings
    ui.card(
        ui.card_header(
            "Test 1: Basic Divider (defaults)",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_left1",
                    label="Left",
                    icon=icon_svg("align-left"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_right1",
                    label="Right",
                    icon=icon_svg("align-right"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_divider() with default width (2px) and gap (1rem)"),
        ),
    ),
    # Test 2: Custom divider width
    ui.card(
        ui.card_header(
            "Test 2: Custom Divider Width",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_left2",
                    label="Button A",
                    icon=icon_svg("a"),
                ),
                ui.toolbar_divider(width="5px"),
                ui.toolbar_input_button(
                    "btn_right2",
                    label="Button B",
                    icon=icon_svg("b"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_divider(width='5px') - wider divider line"),
        ),
    ),
    # Test 3: Custom divider gap
    ui.card(
        ui.card_header(
            "Test 3: Custom Divider Gap",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_left3",
                    label="Button 1",
                    icon=icon_svg("1"),
                ),
                ui.toolbar_divider(gap="2rem"),
                ui.toolbar_input_button(
                    "btn_right3",
                    label="Button 2",
                    icon=icon_svg("2"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_divider(gap='2rem') - more spacing around divider"),
        ),
    ),
    # Test 4: Custom width and gap
    ui.card(
        ui.card_header(
            "Test 4: Custom Width and Gap",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_left4",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                ui.toolbar_divider(width="3px", gap="1.5rem"),
                ui.toolbar_input_button(
                    "btn_right4",
                    label="Load",
                    icon=icon_svg("folder-open"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_divider(width='3px', gap='1.5rem')"),
        ),
    ),
    # Test 5: No visible divider line
    ui.card(
        ui.card_header(
            "Test 5: No Visible Line (spacing only)",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_left5",
                    label="Left",
                    icon=icon_svg("arrow-left"),
                ),
                ui.toolbar_divider(width="0px", gap="2rem"),
                ui.toolbar_input_button(
                    "btn_right5",
                    label="Right",
                    icon=icon_svg("arrow-right"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p(
                "Tests toolbar_divider(width='0px', gap='2rem') - spacing without line"
            ),
        ),
    ),
    # Test 6: Multiple dividers
    ui.card(
        ui.card_header(
            "Test 6: Multiple Dividers",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_multi1",
                    label="One",
                    icon=icon_svg("1"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_multi2",
                    label="Two",
                    icon=icon_svg("2"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_multi3",
                    label="Three",
                    icon=icon_svg("3"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_multi4",
                    label="Four",
                    icon=icon_svg("4"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests multiple dividers in a single toolbar"),
        ),
    ),
    # Test 7: Basic spacer
    ui.card(
        ui.card_header(
            "Test 7: Basic Spacer",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_spacer_left",
                    label="Left",
                    icon=icon_svg("align-left"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_spacer_right",
                    label="Right",
                    icon=icon_svg("align-right"),
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_spacer() - pushes remaining items to the right"),
        ),
    ),
    # Test 8: Spacer with multiple items on each side
    ui.card(
        ui.card_header(
            "Test 8: Spacer with Multiple Items",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_spacer_left1",
                    label="Save",
                    icon=icon_svg("floppy-disk"),
                ),
                ui.toolbar_input_button(
                    "btn_spacer_left2",
                    label="Open",
                    icon=icon_svg("folder-open"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_spacer_right1",
                    label="Settings",
                    icon=icon_svg("gear"),
                ),
                ui.toolbar_input_button(
                    "btn_spacer_right2",
                    label="Help",
                    icon=icon_svg("circle-question"),
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_spacer() with multiple buttons on each side"),
        ),
    ),
    # Test 9: Divider + Spacer combination
    ui.card(
        ui.card_header(
            "Test 9: Divider and Spacer Combined",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_combo_left1",
                    label="Undo",
                    icon=icon_svg("rotate-left"),
                ),
                ui.toolbar_input_button(
                    "btn_combo_left2",
                    label="Redo",
                    icon=icon_svg("rotate-right"),
                ),
                ui.toolbar_divider(),
                ui.toolbar_input_button(
                    "btn_combo_left3",
                    label="Cut",
                    icon=icon_svg("scissors"),
                ),
                ui.toolbar_input_button(
                    "btn_combo_left4",
                    label="Copy",
                    icon=icon_svg("copy"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_combo_right1",
                    label="Search",
                    icon=icon_svg("magnifying-glass"),
                ),
                align="left",
                width="100%",
            ),
        ),
        ui.card_body(
            ui.p("Tests combining toolbar_divider() and toolbar_spacer()"),
        ),
    ),
    # Test 10: Multiple spacers (edge case - only first should work)
    ui.card(
        ui.card_header(
            "Test 10: Multiple Spacers (Edge Case)",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_edge1",
                    label="First",
                    icon=icon_svg("1"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_edge2",
                    label="Middle",
                    icon=icon_svg("2"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_edge3",
                    label="Last",
                    icon=icon_svg("3"),
                ),
                align="left",
            ),
        ),
        ui.card_body(
            ui.p(
                "Tests multiple spacers - only first spacer should add margin-left: auto"
            ),
        ),
    ),
    # Test 11: Dividers with varying custom properties
    ui.card(
        ui.card_header(
            "Test 11: Dividers with Different Custom Properties",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_var1",
                    label="A",
                    icon=icon_svg("a"),
                ),
                ui.toolbar_divider(width="1px", gap="0.5rem"),
                ui.toolbar_input_button(
                    "btn_var2",
                    label="B",
                    icon=icon_svg("b"),
                ),
                ui.toolbar_divider(width="4px", gap="1rem"),
                ui.toolbar_input_button(
                    "btn_var3",
                    label="C",
                    icon=icon_svg("c"),
                ),
                ui.toolbar_divider(width="2px", gap="2rem"),
                ui.toolbar_input_button(
                    "btn_var4",
                    label="D",
                    icon=icon_svg("d"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests multiple dividers with different width and gap values"),
        ),
    ),
    # Test 12: Spacer with align="right" (spacer should still work)
    ui.card(
        ui.card_header(
            "Test 12: Spacer with align='right'",
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_align_left",
                    label="Left Item",
                    icon=icon_svg("align-left"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_align_right",
                    label="Right Item",
                    icon=icon_svg("align-right"),
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.p("Tests toolbar_spacer() with align='right' on toolbar"),
        ),
    ),
    # Test 13: Spacer with explicit width parameter
    ui.card(
        ui.card_header("Test 13: Spacer with Explicit Width Parameter"),
        ui.card_body(
            ui.p("Toolbars with spacers need width='100%' parameter:"),
            ui.toolbar(
                ui.toolbar_input_button(
                    "btn_explicit_left",
                    label="Start",
                    icon=icon_svg("play"),
                ),
                ui.toolbar_spacer(),
                ui.toolbar_input_button(
                    "btn_explicit_right",
                    label="Stop",
                    icon=icon_svg("stop"),
                ),
                width="100%",
            ),
        ),
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
