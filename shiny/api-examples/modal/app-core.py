from shiny import App, Inputs, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("show", "Show modal dialog"),
)


def server(input: Inputs):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        m = ui.modal(
            "This is a somewhat important message.",
            title="Somewhat important message",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(m)


app = App(app_ui, server)
