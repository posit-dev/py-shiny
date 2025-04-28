from shiny import reactive
from shiny.express import module, render, ui


# ============================================================
# Counter module
# ============================================================
@module
def counter(input, output, session, label, starting_value: int = 0):
    count = reactive.value(starting_value)
    with ui.card():
        ui.h2(f"This is {label}")
        ui.input_action_button("button", f"{label}")

        @render.text
        def out():
            return f"Click count is {count()}"

    @reactive.effect
    @reactive.event(input.button)
    def _():
        count.set(count() + 1)


# =============================================================================
# App that uses module
# =============================================================================
counter("counter1", "Counter 1", starting_value=0)
ui.hr()
counter("counter2", "Counter 2", starting_value=0)
