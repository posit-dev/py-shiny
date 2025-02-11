import asyncio

import requests

from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Shiny's README.md"),
        ui.output_markdown_stream("shiny_readme"),
        height="400px",
        class_="mt-3",
        full_screen=True,
    ),
)


def server(input, output, session):
    # Read in the README.md file from the py-shiny repository
    readme = requests.get(
        "https://raw.githubusercontent.com/posit-dev/py-shiny/refs/heads/main/README.md"
    )
    readme_chunks = readme.text.replace("\n", " \n ").split(" ")

    # Generate words from the README.md file (with a small delay)
    async def chunk_generator():
        for chunk in readme_chunks:
            await asyncio.sleep(0.02)
            yield chunk + " "

    md = ui.MarkdownStream("shiny_readme")

    @reactive.effect
    async def _():
        await md.stream(chunk_generator())


app = App(app_ui, server)
