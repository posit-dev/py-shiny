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
def counter_module_ui(id: str):
    return "<HTML>"

def counter_module_server(session: ShinySessionProxy):
    count: ReactiveVal[int] = ReactiveVal(0)

    @observe()
    def on_click():
        session.input['button']
        isolate(lambda: count(count() + 1))

    @session.output("out")
    def out() -> str:
        return f"Click count is {count()}"

counter_module = ShinyModule(counter_module_ui, counter_module_server)


# =============================================================================
# App that uses module
# =============================================================================
def ui():
    counter_module.ui("counter1")
    return "<HTML>"

def server(session: ShinySession):
    counter_module.server("counter1")
    counter_module.server("counter2")

ui_path = os.path.join(os.path.dirname(__file__), "www")

app = ShinyApp(ui_path, server)


if __name__ == "__main__":
    app.run()
