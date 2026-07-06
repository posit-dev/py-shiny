from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h2("Toolbar Input Select Examples"),
    ui.p(
        "Examples showing different ways to configure toolbar_input_select: basic, with icon and tooltip, and grouped choices."
    ),
    ui.card(
        ui.card_header(
            "Basic Select",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="select",
                    label="Choose option",
                    choices=["Option 1", "Option 2", "Option 3"],
                    selected="Option 2",
                ),
                align="right",
            ),
        ),
        ui.card_body(
            ui.output_text("output_example1"),
        ),
    ),
    ui.card(
        ui.card_header(
            "With Icon and Tooltip",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="filter",
                    label="Filter",
                    choices=["All", "Active", "Archived"],
                    icon=icon_svg("filter"),
                    tooltip="Filter the data",
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
            "Grouped Choices",
            ui.toolbar(
                ui.toolbar_input_select(
                    id="grouped",
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
            ui.output_text("output_example3"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def output_example1():
        return f"Selected: {input.select()}"

    @output
    @render.text
    def output_example2():
        return f"Filter: {input.filter()}"

    @output
    @render.text
    def output_example3():
        return f"Selected: {input.grouped()}"


app = App(app_ui, server)
