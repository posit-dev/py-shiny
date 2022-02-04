from shiny import *

# =============================================================================
# Counter module
# =============================================================================
def counter_module_ui(
    ns: Callable[[str], str], label: str = "Increment counter"
) -> TagChildArg:
    return TagList(
        input_action_button(id=ns("button"), label=label),
        output_text_verbatim(id=ns("out")),
    )


def counter_module_server(session: SessionProxy):
    count: ReactiveVal[int] = ReactiveVal(0)

    @observe()
    def _():
        session.input["button"]
        with isolate():
            count(count() + 1)

    @session.output("out")
    def _() -> str:
        return f"Click count is {count()}"


counter_module = ShinyModule(counter_module_ui, counter_module_server)


# =============================================================================
# App that uses module
# =============================================================================
ui = page_fluid(
    counter_module.ui("counter1", "Counter 1"),
    counter_module.ui("counter2", "Counter 2"),
)


def server(session: Session):
    counter_module.server("counter1")
    counter_module.server("counter2")


app = App(ui, server)
