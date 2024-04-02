# Import the custom renderer implementations
from renderers import render_capitalize, render_upper

from shiny.express import input, ui

ui.h1("Capitalization renderer")
ui.input_text("caption", "Caption:", "Data summary")

"@render_upper:"


# Hovering over `@render_upper` will display the class documentation
@render_upper
def upper():
    return input.caption()


"@render_upper():"


# Hovering over `@render_upper` will display the class documentation as there is no
# `__init__()` documentation
@render_upper()
def upper_with_paren():
    return input.caption()


"@render_capitalize:"


# Hovering over `@render_capitalize` will display the class documentation
@render_capitalize
def cap_upper():
    return input.caption()


"@render_capitalize(to='lower'): "


# Hovering over `@render_capitalize` will display the `__init__()` documentation
@render_capitalize(to_case="lower")
def cap_lower():
    return input.caption()
