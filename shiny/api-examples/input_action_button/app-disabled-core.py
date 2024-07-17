from shiny import App, Inputs, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_text("name", "Your Name"),
    ui.input_action_button("greet", "Say Hello", disabled=True),
    ui.output_ui("hello"),
)


def server(input: Inputs):
    @reactive.effect
    @reactive.event(input.name)
    def set_button_state():
        if input.name():
            ui.update_action_button("greet", disabled=False)
        else:
            ui.update_action_button("greet", disabled=True)

    @render.ui
    @reactive.event(input.greet)
    def hello():
        return ui.p(f"Hello, {input.name()}!", class_="fs-1 text-primary mt-3")


app = App(app_ui, server)
