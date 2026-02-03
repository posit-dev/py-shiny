from faicons import icon_svg

from shiny.express import input, render, ui

ui.h2("Toolbar Input Select Examples")
ui.p(
    "Examples showing different ways to configure toolbar_input_select: basic, with icon and tooltip, and grouped choices."
)

with ui.card():
    with ui.card_header():
        "Basic Select"
        with ui.toolbar(align="right"):
            ui.toolbar_input_select(
                id="select",
                label="Choose option",
                choices=["Option 1", "Option 2", "Option 3"],
                selected="Option 2",
            )

    with ui.card_body():

        @render.text
        def output_example1():
            return f"Selected: {input.select()}"


with ui.card():
    with ui.card_header():
        "With Icon and Tooltip"
        with ui.toolbar(align="right"):
            ui.toolbar_input_select(
                id="filter",
                label="Filter",
                choices=["All", "Active", "Archived"],
                icon=icon_svg("filter"),
                tooltip="Filter the data",
            )

    with ui.card_body():

        @render.text
        def output_example2():
            return f"Filter: {input.filter()}"


with ui.card():
    with ui.card_header():
        "Grouped Choices"
        with ui.toolbar(align="right"):
            ui.toolbar_input_select(
                id="grouped",
                label="Select item",
                choices={
                    "Group A": {"a1": "Choice A1", "a2": "Choice A2"},
                    "Group B": {"b1": "Choice B1", "b2": "Choice B2"},
                },
            )

    with ui.card_body():

        @render.text
        def output_example3():
            return f"Selected: {input.grouped()}"
