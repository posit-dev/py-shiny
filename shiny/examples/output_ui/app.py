from shiny import *

app_ui = ui.page_fluid(
    ui.input_action_button("add", "Add more controls"),
    ui.output_ui("moreControls"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_ui()
    @event(input.add)
    def moreControls():
        return ui.TagList(
            ui.input_slider("n", "N", 1, 1000, 500), ui.input_text("label", "Label")
        )


app = App(app_ui, server)
