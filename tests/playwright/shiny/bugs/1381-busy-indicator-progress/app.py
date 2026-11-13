import time

from shiny import App, Inputs, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("rerender", "Re-render"),
    ui.output_text("out1"),
    ui.output_text("out2"),
    ui.output_text("out3"),
    ui.output_text("out4"),
)


def server(input: Inputs):
    def slow_value() -> str:
        n = input.rerender()
        # Block the event loop, as the plots in #1381 did.
        time.sleep(0.5)
        return str(n)

    @render.text
    def out1():
        return slow_value()

    @render.text
    def out2():
        return slow_value()

    @render.text
    def out3():
        return slow_value()

    @render.text
    def out4():
        return slow_value()


app = App(app_ui, server)
