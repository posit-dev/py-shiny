from shiny import reactive
from shiny.express import input, ui

with ui.layout_column_wrap(width=1 / 2):
    ui.input_radio_buttons("pet_type", "Pet type", ["Dog", "Cat", "Bird"], inline=True)
    ui.input_radio_buttons("pet_sex", "Pet sex", ["Male", "Female"], inline=True)
    ui.input_text("name", "Pet name", "Charlie")
    ui.input_text("royal_name", "Royal Name", "King Charlie")


@reactive.effect
@reactive.event(input.pet_type)
def _():
    # Update the label of the pet name input
    ui.update_text("name", label=f"{input.pet_type()}'s name")


@reactive.effect
def _():
    # Update the value of the royal name input
    royal_noun = "King" if input.pet_sex() == "Male" else "Queen"
    ui.update_text("royal_name", value=f"{royal_noun} {input.name()}")
