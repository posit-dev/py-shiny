from shiny import *

# ============================================================
# Counter module
# ============================================================
def counter_module_ui(
    ns: Callable[[str], str], label: str = "Increment counter"
) -> TagChildArg:
    return ui.div(
        {"style": "border: 1px solid #ccc; border-radius: 5px; margin: 5px 0;"},
        ui.h2("This is " + label),
        ui.input_action_button(id=ns("button"), label=label),
        ui.output_text_verbatim(id=ns("out")),
    )


def counter_module_server(
    input: InputsProxy, output: OutputsProxy, session: SessionProxy
):
    count: reactive.Value[int] = reactive.Value(0)

    @reactive.effect()
    @event(input.button)
    def _():
        count.set(count() + 1)

    @output()
    @render_text()
    def out() -> str:
        return f"Click count is {count()}"


counter_module = ShinyModule(counter_module_ui, counter_module_server)


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    counter_module.ui("counter1", "Counter 1"),
    counter_module.ui("counter2", "Counter 2"),
)


def server(input: Inputs, output: Outputs, session: Session):
    counter_module.server("counter1")
    counter_module.server("counter2")


app = App(app_ui, server)
