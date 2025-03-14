from shiny.express import input, render, ui

# Sample data for different types of choices
simple_choices = ["A", "B", "C", "D"]
dict_choices = {"a": "Option A", "b": "Option B", "c": "Option C"}
grouped_choices = {
    "Group 1": {"g1a": "Group 1 - A", "g1b": "Group 1 - B"},
    "Group 2": {"g2a": "Group 2 - A", "g2b": "Group 2 - B"},
}

# Page options
ui.page_opts(fillable=True)

with ui.layout_column_wrap(width="400px"):
    # Basic select with simple choices
    with ui.card():
        ui.card_header("Basic Select")
        ui.input_select(
            id="select1",
            label="Basic select (simple list)",
            choices=simple_choices,
            selected="A",
        )

        @render.text
        def selected_value1():
            return f"Selected: {input.select1()}"

    # Select with dictionary choices
    with ui.card():
        ui.card_header("Dictionary Choices")
        ui.input_select(
            id="select2",
            label="Select with dictionary choices",
            choices=dict_choices,
            selected="a",
        )

        @render.text
        def selected_value2():
            return f"Selected: {input.select2()}"

    # Select with grouped choices
    with ui.card():
        ui.card_header("Grouped Choices")
        ui.input_select(
            id="select3",
            label="Select with grouped choices",
            choices=grouped_choices,
            selected="g1a",
        )

        @render.text
        def selected_value3():
            return f"Selected: {input.select3()}"

    # Multiple select
    with ui.card():
        ui.card_header("Multiple Select")
        ui.input_select(
            id="select4",
            label="Multiple select",
            choices=simple_choices,
            selected=["A", "B"],
            multiple=True,
        )

        @render.text
        def selected_value4():
            return f"Selected: {input.select4()}"

    # Select with custom width
    with ui.card():
        ui.card_header("Custom Width")
        ui.input_select(
            id="select5",
            label="Select with custom width",
            choices=simple_choices,
            width="200px",
        )

        @render.text
        def selected_value5():
            return f"Selected: {input.select5()}"

    # Select with size parameter
    with ui.card():
        ui.card_header("Box Style")
        ui.input_select(
            id="select6",
            label="Select with size parameter",
            choices=simple_choices,
            size="4",  # Shows 4 items at once
        )

        @render.text
        def selected_value6():
            return f"Selected: {input.select6()}"
