import time

import requests

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.output_markdown_stream("shiny-readme"),
)


def server(input, output, session):
    # Read in the README.md file from the py-shiny repository
    readme = requests.get(
        "https://raw.githubusercontent.com/posit-dev/py-shiny/refs/heads/main/README.md"
    )
    readme_chunks = readme.text.replace("\n", " \n ").split(" ")

    # Generate words from the README.md file (with a small delay)
    def chunk_generator():
        for chunk in readme_chunks:
            time.sleep(0.05)
            yield chunk + " "

    md = ui.MarkdownStream("shiny-readme")
    md.stream(chunk_generator())


app = App(app_ui, server)
