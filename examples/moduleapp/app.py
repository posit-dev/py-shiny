from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


# ============================================================
# Counter module
# ============================================================
@module.ui
def counter_ui(label: str = "Increment counter") -> ui.TagChild:
    return ui.card(
        ui.h2("This is " + label),
        ui.input_action_button(id="button", label=label),
        ui.output_code(id="out"),
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

    @render.code
    def out() -> str:
        return f"Click count is {count()}"


# ============================================================
# Counter Wrapper module -- shows that counter still works
# the same way when wrapped in a dynamic UI
# ============================================================
@module.ui
def counter_wrapper_ui() -> ui.TagChild:
    return ui.output_ui("dynamic_counter")


@module.server
def counter_wrapper_server(
    input: Inputs, output: Outputs, session: Session, label: str = "Increment counter"
):
    @render.ui()
    def dynamic_counter():
        return counter_ui("counter", label)

    counter_server("counter")


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    counter_ui("counter1", "Counter 1"),
    counter_wrapper_ui("counter2_wrapper"),
    ui.output_ui("counter3_ui"),
)


def server(input: Inputs, output: Outputs, session: Session):
    counter_server("counter1")
    counter_wrapper_server("counter2_wrapper", "Counter 2")

    @render.ui()
    def counter3_ui():
        counter_server("counter3")
        return counter_ui("counter3", "Counter 3")

    counter_server("counter")


app = App(app_ui, server)
