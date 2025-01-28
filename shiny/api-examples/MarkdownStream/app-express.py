import time

import requests

from shiny.express import session, ui

# Read in the README.md file from the py-shiny repository
readme = requests.get(
    "https://raw.githubusercontent.com/posit-dev/py-shiny/refs/heads/main/README.md"
)
readme_chunks = readme.text.replace("\n", " \n ").split(" ")


# Generate words from the README.md file (with a small delay)
def chunk_generator():
    for chunk in readme_chunks:
        if not session.is_stub_session():
            time.sleep(0.02)
        yield chunk + " "


md = ui.MarkdownStream("shiny-readme")

with ui.card(height="400px"):
    ui.card_header("Shiny README.md")
    md.ui()

md.stream(chunk_generator())
