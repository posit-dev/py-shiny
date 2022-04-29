from shiny import *

# ============================================================
# Counter module
# ============================================================
@module_ui
def counter_ui(label: str = "Increment counter") -> ui.TagChildArg:
    return ui.div(
        {"style": "border: 1px solid #ccc; border-radius: 5px; margin: 5px 0;"},
        ui.h2("This is " + label),
        ui.input_action_button(id="button", label=label),
        ui.output_text_verbatim(id="out"),
    )


@module_server
def counter_server(input: Inputs, output: Outputs, session: Session) -> int:
    count: reactive.Value[int] = reactive.Value(0)

    @reactive.Effect
    @event(input.button)
    def _():
        count.set(count() + 1)

    @output
    @render.text
    def out() -> str:
        return f"Click count is {count()}"

    return 1


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    counter_ui("counter1", "Counter 1"),
    counter_ui("counter2", "Counter 2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    counter_server("counter1")
    val = counter_server("counter2")
    print(val)


app = App(app_ui, server)
