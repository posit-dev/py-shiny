from shiny.express import input, render, ui

ui.page_opts(title="Select Inputs Kitchensink")

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


with ui.card():
    ui.input_select("basic_select", "Default select", fruits)

    @render.code
    def basic_result_txt():
        return input.basic_select()


with ui.card():
    ui.input_select("multi_select", "Multiple Select", fruits, multiple=True)

    @render.code
    def multi_result_txt():
        return ", ".join(input.multi_select())


with ui.card():
    ui.input_select(
        "select_with_selected", "Select with selected", fruits, selected="Cherry"
    )

    @render.code
    def select_with_selected_txt():
        return str(input.select_with_selected())


with ui.card():
    ui.input_select("width_select", "Select with Custom Width", fruits, width="400px")

    @render.code
    def width_result_txt():
        return str(input.width_select())


with ui.card():
    ui.input_select(
        "select_with_labels",
        "Select with labels",
        fruits_dict,
    )

    @render.code
    def select_with_labels_txt():
        return str(input.select_with_labels())


with ui.card():
    ui.input_select(
        "select_with_custom_size_and_dict",
        "Select with custom size and dict",
        fruits_grouped_dict,
        size="4",
    )

    @render.code
    def select_with_custom_size_and_dict_txt():
        return str(input.select_with_custom_size_and_dict())
