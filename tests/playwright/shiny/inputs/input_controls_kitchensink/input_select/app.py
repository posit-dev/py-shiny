from shiny.express import input, render, ui

ui.page_opts(title="Multiple Select Inputs Demo")

fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
fruits_dict = {
    "Citrus": {
        "Orange": "Sweet and tangy",
        "Lemon": "Zesty and refreshing",
        "Lime": "Bright and tart",
    },
    "Berries": {
        "Strawberry": "Juicy and sweet",
        "Blueberry": "Tiny and antioxidant-rich",
        "Raspberry": "Delicate and slightly tart",
    },
}


with ui.card():
    ui.input_select("basic_select", "Default select", fruits)

with ui.card():
    ui.input_select("multi_select", "Multiple Select", fruits, multiple=True)

with ui.card():
    ui.input_select(
        "select_with_selected", "Select with selected", fruits, selected="Cherry"
    )

with ui.card():
    ui.input_select("width_select", "Select with Custom Width", fruits, width="400px")

with ui.card():
    ui.input_select(
        "select_with_custom_size_and_dict",
        "Select with custom size and dict",
        fruits_dict,
        size="4",
    )


@render.text
def basic_result_txt():
    return f"Basic select: {input.basic_select()}"


@render.text
def multi_result_txt():
    return f"Multi select: {', '.join(input.multi_select())}"


@render.text
def default_result_txt():
    return f"Select with selected: {input.select_with_selected()}"


@render.text
def width_result_txt():
    return f"Width select: {input.width_select()}"


@render.text
def placeholder_result_txt():
    return f"Dict and custom select: {input.select_with_custom_size_and_dict()}"
