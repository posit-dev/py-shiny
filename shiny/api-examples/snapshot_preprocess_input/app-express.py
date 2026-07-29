from shiny import render
from shiny.express import input, ui
from shiny.testmode import snapshot_preprocess_input

ui.input_text("secret", "Secret", value="hunter2")

# Scrub the sensitive value from test-mode snapshots; the live input value is
# untouched. Has no effect unless test mode is enabled (`SHINY_TESTMODE=1`),
# so the call can be left in production code.
snapshot_preprocess_input("secret", lambda value: "<redacted>")


@render.text
def shout() -> str:
    return str(input.secret()).upper()
