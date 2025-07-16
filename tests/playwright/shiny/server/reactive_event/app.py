from __future__ import annotations

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h2(ui.code("@reactive.event")),
    ui.input_action_button("btn_count", "Immediate Count"),
    ui.tags.br(),
    ui.tags.label("Rendered on click:"),
    ui.output_text_verbatim("txt_immediate", placeholder=True),
    ui.input_action_button("btn_trigger", "Update Count"),
    ui.tags.br(),
    ui.tags.label("Reactive event on renderer:"),
    ui.output_text_verbatim("txt_render_delayed", placeholder=True),
    ui.tags.label("Reactive event on reactive calc:"),
    ui.output_text_verbatim("txt_reactive_delayed", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def txt_immediate():
        return input.btn_count()

    @render.text
    @reactive.event(input.btn_trigger)
    def txt_render_delayed():
        return input.btn_count()

    @reactive.calc()
    @reactive.event(input.btn_trigger)
    def delayed_btn_count() -> int:
        return input.btn_count()

    @render.text
    def txt_reactive_delayed():
        return str(delayed_btn_count())


app = App(app_ui, server)
