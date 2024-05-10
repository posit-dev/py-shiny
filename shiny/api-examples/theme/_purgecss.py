# flake8: noqa E402
# This file is used to create a minimal Bootstrap CSS file based on a custom Bootstrap
# theme created with ui.Theme*().

# NOTE: This script requires the `purgecss` package to be installed.
#       You can install it with `npm install -g purgecss`.

import shutil
import subprocess
from pathlib import Path

from shared import filler_text, my_theme

my_theme.name = "demo"

from shiny import ui

# If __file__ is not defined, use the current working directory
if not globals().get("__file__"):
    __file__ = Path.cwd() / "_purgecss.py"


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_numeric("n", "N", min=0, max=100, value=20),
        title="Parameters",
    ),
    ui.h2("Output"),
    ui.output_text_verbatim("txt"),
    ui.markdown(filler_text),
    title="Theme Example",
    theme=my_theme,
)


save_dir = Path(__file__).parent / "output"
if save_dir.exists():
    shutil.rmtree(save_dir)
save_dir.mkdir()
app_ui.save_html(save_dir / "index.html", include_version=False)

purged_dir = Path(__file__).parent / "css"
purged_dir.mkdir(exist_ok=True)

args = [
    "purgecss",
    "--variables",
    "--css",
    "output/lib/shiny-theme-demo/shiny-theme-demo.min.css",
    "--content",
    "output/index.html",
    "--output",
    "css",
]

subprocess.run(args)

(purged_dir / "shiny-theme-demo.min.css").rename(purged_dir / "shiny-theme-demo.css")

if True:
    shutil.rmtree(save_dir)
