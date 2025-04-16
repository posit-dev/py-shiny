from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


# ============================================================
# Counter module
# ============================================================
@module.ui
def counter_ui(label: str = "Increment counter") -> ui.TagChild:
    return ui.card(
        ui.h2("This is " + label),
        ui.input_action_button(id="button", label=label),
        ui.output_text(id="out"),
    )


@module.server
def counter_server(
    input: Inputs, output: Outputs, session: Session, starting_value: int = 0
):
    count: reactive.value[int] = reactive.value(starting_value)

    @reactive.effect
    @reactive.event(input.button)
    def _():
        count.set(count() + 1)

    @render.text
    def out() -> str:
        return f"Click count is {count()}"


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    counter_ui("counter1", "Counter 1"),
    counter_ui("counter2", "Counter 2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    counter_server("counter1")
    counter_server("counter2")


app = App(app_ui, server)
