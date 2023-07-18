import random

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.markdown(
        f"""
        This example demonstrates how `@reactive.event()` can be used to restrict
        execution of: (1) a `@render` function, (2) `@reactive.Calc`, or (3)
        `@reactive.Effect`.

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

    @reactive.Effect
    def _():
        reactive.invalidate_later(0.5)
        val.set(random.randint(0, 1000))

    # Always update this output when the number is updated
    @output
    @render.ui
    def number():
        return val.get()

    # Since ignore_none=False, the function executes before clicking the button.
    # (input.btn_out() is 0 on page load, but @@reactive.event() treats 0 as None for
    # action buttons.)
    @output
    @render.text
    @reactive.event(input.btn_out, ignore_none=False)
    def out_out():
        return str(val.get())

    @reactive.Calc
    @reactive.event(input.btn_calc)
    def calc():
        return 1 / val.get()

    @output
    @render.text
    def out_calc():
        return str(calc())

    @reactive.Effect
    @reactive.event(input.btn_effect)
    def _():
        ui.insert_ui(
            ui.p("Random number!", val.get()),
            selector="#out_effect",
            where="afterEnd",
        )


app = App(app_ui, server)
