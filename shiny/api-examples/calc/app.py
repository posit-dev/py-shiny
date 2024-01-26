import random
import time

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.layout_columns(
            ui.input_action_button("first", "Invalidate first (slow) computation"),
            ui.input_action_button("second", "Invalidate second (fast) computation"),
        ),
        ui.output_text_verbatim("result"),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
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

    @render.text
    def result():
        return first() + second()


app = App(app_ui, server)
