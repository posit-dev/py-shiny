from shiny import reactive
from shiny.express import module, render, ui


@module
def counter(input, output, session, starting_value: int = 0):
    count = reactive.value(starting_value)

    ui.input_action_button("btn", "Increment")

    with ui.div():

        @render.express
        def current_count():
            count()

    @reactive.effect
    @reactive.event(input.btn)
    def increment():
        count.set(count() + 1)


counter("one")
ui.hr()
counter("two")
