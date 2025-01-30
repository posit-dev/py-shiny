from pathlib import Path

from shiny.express import ui

# Read in the py-shiny README.md file
readme = Path(__file__).parent / "README.md"
with open(readme, "r") as f:
    readme_chunks = f.read().replace("\n", " \n ").split(" ")


stream = ui.MarkdownStream("shiny-readme")
stream2 = ui.MarkdownStream("shiny-readme-err")


def readme_generator():
    for chunk in readme_chunks:
        yield chunk + " "


def readme_generator_err():
    for chunk in readme_chunks:
        yield chunk + " "
        if chunk == "Shiny":
            raise RuntimeError("boom!")


stream.stream(readme_generator())
stream2.stream(readme_generator_err())


with ui.card(
    height="400px",
    class_="mt-3",
):
    ui.card_header("Shiny README.md")
    stream.ui()


with ui.card(class_="mt-3"):
    ui.card_header("Shiny README.md with error")
    stream2.ui()
