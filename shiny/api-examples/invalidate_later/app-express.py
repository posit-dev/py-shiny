import random

from shiny import reactive
from shiny.express import render


@render.text
def value():
    reactive.invalidate_later(0.5)
    return "Random int: " + str(random.randint(0, 10000))
