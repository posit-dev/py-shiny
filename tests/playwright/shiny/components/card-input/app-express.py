from shiny.express import input, render, ui

with ui.card(id="my_card", full_screen=True):
    ui.card_header("Hello, card!")
    "A regular full-screenable card."

with ui.value_box(
    id="my_value_box",
    full_screen=True,
    showcase=ui.span("$", class_="fs-1"),
):
    "Hello, value box!"
    "$1,234,567"


@render.code()
def out_card():
    return f"{input.my_card_full_screen()!r}"


@render.code()
def out_value_box():
    return f"{input.my_value_box_full_screen()!r}"
