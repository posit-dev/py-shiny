import time

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


@module.ui
def button_ui():
    return ui.TagList(
        ui.input_task_button("btn", label="Go"),
        ui.output_text("text_counter"),
    )


@module.server
def button_server(input: Inputs, output: Outputs, session: Session):
    counter = reactive.value(0)

    @render.text
    def text_counter():
        return f"Button clicked {counter()} times"

    @reactive.effect
    @reactive.event(input.btn)
    def increment_counter():
        time.sleep(0.5)
        counter.set(counter() + 1)


app_ui = ui.page_fluid(button_ui("mod1"))


def server(input: Inputs, output: Outputs, session: Session):
    button_server("mod1")


app = App(app_ui, server)
