from shiny.express import input, render, ui

ui.page_opts(title="Selectize Inputs kitchensink")

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


ui.input_selectize("basic_selectize", "Default selectize", fruits)


ui.input_selectize("multi_selectize", "Multiple Selectize", fruits, multiple=True)


ui.input_selectize(
    "selectize_with_selected", "Selectize with selected", fruits, selected="Cherry"
)


ui.input_selectize(
    "selectize_width_close_button",
    "Selectize with Custom Width and remove btn",
    fruits_dict,
    width="400px",
    remove_button=True,
)


@render.text
def basic_result_txt():
    return f"Basic select: {input.basic_selectize()}"


@render.text
def multi_result_txt():
    return f"Multi select: {', '.join(input.multi_selectize())}"


@render.text
def selected_result_txt():
    return f"Select with selected: {input.selectize_with_selected()}"


@render.text
def selectize_width_close_button_txt():
    return f"Selectize with close button: {input.selectize_width_close_button()}"
