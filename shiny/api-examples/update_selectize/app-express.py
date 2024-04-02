from shiny import reactive
from shiny.express import ui

ui.input_selectize("x", "Server side selectize", choices=[], multiple=True)


@reactive.effect
def _():
    ui.update_selectize(
        "x",
        choices=[f"Foo {i}" for i in range(10000)],
        selected=["Foo 0", "Foo 1"],
        server=True,
    )
