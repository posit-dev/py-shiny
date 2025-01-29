from pathlib import Path

from shiny.express import ui

readme = Path(__file__).parent / "README.md"
with open(readme, "r") as f:
    readme_chunks = f.read().replace("\n", " \n ").split(" ")


# Generate words from the README.md file (with a small delay)
def chunk_generator():
    for chunk in readme_chunks:
        yield chunk + " "


md = ui.MarkdownStream("shiny-readme")

with ui.card(
    height="400px",
    class_="mt-3",
):
    ui.card_header("Shiny README.md")
    md.ui()

md.stream(chunk_generator())
