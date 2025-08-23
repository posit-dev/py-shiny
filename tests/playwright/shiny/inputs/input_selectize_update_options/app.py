from shiny import reactive
from shiny.express import input, render, ui

ui.input_selectize(
    "single",
    "Single choice",
    choices=["Option 1", "Option 2", "Option 3"],
    multiple=False,
)

ui.input_selectize(
    "multiple",
    "Multiple choice",
    choices=["Option 1", "Option 2", "Option 3"],
    selected=["Option 1", "Option 2"],
    multiple=True,
)


# Default plugins should be retained on options update
@reactive.effect
def _():
    with reactive.isolate():
        selected = input.single()
    ui.update_selectize(
        "single",
        selected=selected,  # Workaround for https://github.com/rstudio/shiny/issues/4278
        options={"placeholder": "Select an option"},
    )


# Default plugins should be retained on options update
@reactive.effect
def _():
    ui.update_selectize(
        "multiple",
        options={"placeholder": "Select an option"},
    )


@render.code
def single_out():
    return input.single()


@render.code
def multiple_out():
    return ", ".join(input.multiple())
