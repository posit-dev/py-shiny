# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

# Add parent directory to path, so we can find the prism module.
# (This is just a temporary fix)
import os
import sys

# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)

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


def counter_module_server(session: ShinySessionProxy):
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


if __name__ == "__main__":
    app.run()
