from shiny import App, render, ui

# Sample data for different types of choices
simple_choices = ["A", "B", "C", "D"]
dict_choices = {"a": "Option A", "b": "Option B", "c": "Option C"}
grouped_choices = {
    "Group 1": {"g1a": "Group 1 - A", "g1b": "Group 1 - B"},
    "Group 2": {"g2a": "Group 2 - A", "g2b": "Group 2 - B"},
}

app_ui = ui.page_fillable(
    ui.layout_column_wrap(
        # Basic select with simple choices
        ui.card(
            ui.card_header("Basic Select"),
            ui.input_select(
                id="select1",
                label="Basic select (simple list)",
                choices=simple_choices,
                selected="A",
            ),
            ui.output_text("selected_value1"),
        ),
        # Select with dictionary choices
        ui.card(
            ui.card_header("Dictionary Choices"),
            ui.input_select(
                id="select2",
                label="Select with dictionary choices",
                choices=dict_choices,
                selected="a",
            ),
            ui.output_text("selected_value2"),
        ),
        # Select with grouped choices
        ui.card(
            ui.card_header("Grouped Choices"),
            ui.input_select(
                id="select3",
                label="Select with grouped choices",
                choices=grouped_choices,
                selected="g1a",
            ),
            ui.output_text("selected_value3"),
        ),
        # Multiple select
        ui.card(
            ui.card_header("Multiple Select"),
            ui.input_select(
                id="select4",
                label="Multiple select",
                choices=simple_choices,
                selected=["A", "B"],
                multiple=True,
            ),
            ui.output_text("selected_value4"),
        ),
        # Select with custom width
        ui.card(
            ui.card_header("Custom Width"),
            ui.input_select(
                id="select5",
                label="Select with custom width",
                choices=simple_choices,
                width="200px",
            ),
            ui.output_text("selected_value5"),
        ),
        # Select with size parameter
        ui.card(
            ui.card_header("Box Style"),
            ui.input_select(
                id="select6",
                label="Select with size parameter",
                choices=simple_choices,
                size="4",  # Shows 4 items at once
            ),
            ui.output_text("selected_value6"),
        ),
        width="400px",
    ),
)


def server(input, output, session):

    @render.text
    def selected_value1():
        return f"Selected: {input.select1()}"

    @render.text
    def selected_value2():
        return f"Selected: {input.select2()}"

    @render.text
    def selected_value3():
        return f"Selected: {input.select3()}"

    @render.text
    def selected_value4():
        return f"Selected: {input.select4()}"

    @render.text
    def selected_value5():
        return f"Selected: {input.select5()}"

    @render.text
    def selected_value6():
        return f"Selected: {input.select6()}"


app = App(app_ui, server)
