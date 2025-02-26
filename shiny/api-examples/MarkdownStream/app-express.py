import asyncio

import requests

from shiny import reactive
from shiny.express import session, ui

ui.page_opts(full_width=True)

# Initialize a markdown stream object
md = ui.MarkdownStream("shiny_readme")

# Display the stream UI in a card
with ui.card(height="400px", class_="mt-3", full_screen=True):
    ui.card_header("Shiny README.md")
    md.ui()


# Read in the README.md file from the py-shiny repository
readme = requests.get(
    "https://raw.githubusercontent.com/posit-dev/py-shiny/refs/heads/main/README.md"
)
readme_chunks = readme.text.replace("\n", " \n ").split(" ")


# Generate words from the README.md file (with a small delay)
async def chunk_generator():
    for chunk in readme_chunks:
        if not session.is_stub_session():
            await asyncio.sleep(0.02)
        yield chunk + " "


@reactive.effect
async def _():
    await md.stream(chunk_generator())
