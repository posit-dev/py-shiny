from datetime import datetime

from shiny import render
from shiny.express import input, ui

ui.input_text("name", "Name", value="Shiny")


@render.text
def greeting() -> str:
    return f"Hello, {input.name()}! It is {datetime.now().isoformat()}."


# Scrub the nondeterministic timestamp from test-mode snapshots so they diff
# cleanly; the value sent to the client is untouched. Has no effect unless
# test mode is enabled (`SHINY_TESTMODE=1`), so the call can be left in
# production code.
greeting.snapshot_preprocess(lambda value: value.split(" It is ")[0])
