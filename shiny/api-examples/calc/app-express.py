import random
import time

from shiny import reactive
from shiny.express import input, render, ui


@reactive.calc
def first():
    input.first()
    p = ui.Progress()
    for i in range(30):
        p.set(i / 30, message="Computing, please wait...")
        time.sleep(0.1)
    p.close()
    return random.randint(1, 1000)


@reactive.calc
def second():
    input.second()
    return random.randint(1, 1000)


with ui.card():
    with ui.layout_columns():
        ui.input_action_button("first", "Invalidate first (slow) computation")
        ui.input_action_button("second", "Invalidate second (fast) computation")

    @render.text
    def result():
        return first() + second()
