from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("add", "Add more controls"),
    ui.output_ui("moreControls"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    @reactive.event(input.add)
    def moreControls():
        return ui.TagList(
            ui.input_slider("n", "N", min=1, max=1000, value=500),
            ui.input_text("label", "Label"),
        )


app = App(app_ui, server)
