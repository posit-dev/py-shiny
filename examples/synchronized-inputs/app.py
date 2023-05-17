import asyncio
import random

from shiny import *

app_ui = ui.page_fluid(
    ui.input_action_button("shuffle", "Shuffle"),
    ui.output_ui("inputs1"),
    ui.output_ui("inputs2"),
    ui.output_text("out"),
)


def server(input, output, session):
    @reactive.Calc
    def rand():
        input.shuffle()
        return random.randint(0, 1000)

    @output
    @render.ui
    def inputs1():
        input.x.freeze()
        return ui.input_slider("x", "x", min=1, max=1001, value=rand())

    @output
    @render.ui
    def inputs2():
        input.y.freeze()
        return ui.input_numeric("y", "y", min=1, max=1001, value=rand())

    @output
    @render.text
    async def out():
        await asyncio.sleep(0.5)
        if input.x() != input.y():
            raise Exception(f"Inconsistent inputs: {input.x()} {input.y()}")
        if input.x() != rand():
            raise Exception(f"Input doesn't match calc: {input.x()} {rand()}")
        return f"Hello {input.x()} {input.y()}"


app = App(app_ui, server)
