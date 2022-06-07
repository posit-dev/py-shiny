from shiny import *
from shiny.ui import tags

app_ui = ui.page_fluid(
    tags.p(
        """
      The first time you click the button, you should see a 1 appear below the button,
      as well as 2 messages in the python console (all reporting 1 click). After
      clicking once, clicking again should increment the number below the button and
      print the number of clicks in the console twice.
      """
    ),
    ui.input_action_button("btn", "Click me"),
    ui.output_ui("btn_value"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Effect()
    @event(input.btn)
    def _():
        print("@effect() event: ", str(input.btn()))

    @reactive.Calc()
    @event(input.btn)
    def btn() -> int:
        return input.btn()

    @reactive.Effect()
    def _():
        print("@calc() event:   ", str(btn()))

    @output()
    @render.ui()
    @event(input.btn)
    def btn_value():
        return str(input.btn())


app = App(app_ui, server)
