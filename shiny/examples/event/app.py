import random
from shiny import *

app_ui = ui.page_fluid(
    ui.markdown(
        f"""
        This example demonstrates how `@event()` can be used to restrict execution of:
        (1) a `@render` function, (2) `@reactive.Calc`, or (3) `@reactive.Effect`.

        In all three cases, the output is dependent on a random value that gets updated
        every 0.5 seconds (currently, it is {ui.output_ui("number", inline=True)}), but
        the output is only updated when the button is clicked.
        """
    ),
    ui.row(
        ui.column(
            3,
            ui.input_action_button("btn_out", "(1) Update number"),
            ui.output_text("out_out"),
        ),
        ui.column(
            3,
            ui.input_action_button("btn_calc", "(2) Show 1 / number"),
            ui.output_text("out_calc"),
        ),
        ui.column(
            3,
            ui.input_action_button("btn_effect", "(3) Log number"),
            ui.div(id="out_effect"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):

    # Update a random number every second
    val = reactive.Value(random.randint(0, 1000))

    @reactive.Effect()
    def _():
        reactive.invalidate_later(0.5)
        val.set(random.randint(0, 1000))

    # Always update this output when the number is updated
    @output(name="number")
    @render.ui()
    def _():
        return val.get()

    # Since ignore_none=False, the function executes before clicking the button.
    # (input.btn_out() is 0 on page load, but @event() treats 0 as None for action buttons.)
    @output(name="out_out")
    @render.text()
    @event(input.btn_out, ignore_none=False)
    def _():
        return val.get()

    @reactive.Calc()
    @event(input.btn_calc)
    def calc():
        return 1 / val.get()

    @output(name="out_calc")
    @render.text()
    def _():
        return calc()

    @reactive.Effect()
    @event(input.btn_effect)
    def _():
        ui.insert_ui(
            ui.p("Random number!", val.get()),
            selector="#out_effect",
            where="afterEnd",
        )


app = App(app_ui, server)
