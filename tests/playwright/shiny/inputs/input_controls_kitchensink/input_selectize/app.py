from shiny.express import input, render, ui

ui.page_opts(title="Selectize Inputs kitchensink")

fruits = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
fruits_dict = {
    "apple": "Apple",
    "banana": "Banana",
    "cherry": "Cherry",
    "date": "Date",
    "elderberry": "Elderberry",
}

fruits_grouped_dict = {
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


# Currently not wrapping in cards, as opening the selectize within a short card hides the selectize dropdown
ui.input_selectize("basic_selectize", "Default selectize", fruits)


@render.code
def basic_result_txt():
    return str(input.basic_selectize())


ui.input_selectize("selectize_with_label", "Selectize with label", fruits_dict)


@render.code
def selectize_with_label_txt():
    return str(input.selectize_with_label())


ui.input_selectize("multi_selectize", "Multiple Selectize", fruits, multiple=True)


@render.code
def multi_result_txt():
    return ", ".join(input.multi_selectize())


ui.input_selectize(
    "selectize_with_selected",
    "Selectize with selected",
    fruits,
    selected="Cherry",
)


@render.code
def selected_result_txt():
    return str(input.selectize_with_selected())


ui.input_selectize(
    "selectize_width_close_button",
    "Selectize with Custom Width and remove btn",
    fruits_grouped_dict,
    width="400px",
    remove_button=True,
)


@render.code
def selectize_width_close_button_txt():
    return str(input.selectize_width_close_button())
