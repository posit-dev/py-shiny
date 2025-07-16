from shiny import reactive
from shiny.express import input, ui

"The first checkbox group controls the second"
ui.input_checkbox_group(
    "inCheckboxGroup", "Input checkbox", ["Item A", "Item B", "Item C"]
)
ui.input_checkbox_group(
    "inCheckboxGroup2", "Input checkbox 2", ["Item A", "Item B", "Item C"]
)


@reactive.effect
def _():
    x = input.inCheckboxGroup()

    # Can also set the label and select items
    ui.update_checkbox_group(
        "inCheckboxGroup2",
        label="Checkboxgroup label " + str(len(x)),
        choices=x,
        selected=x,
    )
