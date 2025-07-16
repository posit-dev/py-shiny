from shiny.express import input, render, ui

ui.input_slider("n", "N", 1, 100, 50)


# @render.express is like @render.ui, but with Express syntax
@render.express
def render_express1():
    "Slider value:"
    input.n()


# @render.express() also works with parens
@render.express()
def render_express2():
    "Slider value:"
    input.n()
