import random

from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui

ui.markdown(
    f"""
    This example demonstrates how `@reactive.event()` can be used to restrict
    execution of: (1) a `@render` function, (2) `@reactive.calc`, or (3)
    `@reactive.effect`.

    In all three cases, the output is dependent on a random value that gets updated
    every 0.5 seconds (currently, it is {output_ui("number", inline=True)}), but
    the output is only updated when the button is clicked.
    """
)

# Always update this output when the number is updated
with ui.hold():

    @render.ui
    def number():
        return val.get()


ui.input_action_button("btn_out", "(1) Update number")


# Since ignore_none=False, the function executes before clicking the button.
# (input.btn_out() is 0 on page load, but @@reactive.event() treats 0 as None for
# action buttons.)
@render.text
@reactive.event(input.btn_out, ignore_none=False)
def out_out():
    return str(val.get())


ui.input_action_button("btn_calc", "(2) Show 1 / number")


@render.text
def out_calc():
    return str(calc())


ui.input_action_button("btn_effect", "(3) Log number")
ui.div(id="out_effect")


# Update a random number every second
val = reactive.value(random.randint(0, 1000))


@reactive.effect
def _():
    reactive.invalidate_later(0.5)
    val.set(random.randint(0, 1000))


@reactive.calc
@reactive.event(input.btn_calc)
def calc():
    return 1 / val.get()


@reactive.effect
@reactive.event(input.btn_effect)
def _():
    ui.insert_ui(
        ui.p("Random number! ", val.get()),
        selector="#out_effect",
        where="afterEnd",
    )
