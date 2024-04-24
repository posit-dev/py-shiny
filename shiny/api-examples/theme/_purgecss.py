# This file is used to create a minimal Bootstrap CSS file based on the Minty
# Bootstwatch theme for use in the example apps.

# NOTE: This script requires the `purgecss` package to be installed.
#       You can install it with `npm install -g purgecss`.

import shutil
import subprocess
from pathlib import Path

import shinyswatch

from shiny import ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_numeric("n", "N", min=0, max=100, value=20),
        title="Parameters",
    ),
    ui.h2("Output"),
    ui.output_text_verbatim("txt"),
    ui.markdown(
        """
**AI-generated filler text.** In the world of exotic fruits, the durian stands out with its spiky exterior and strong odor. Despite its divisive smell, many people are drawn to its rich, creamy texture and unique flavor profile. This tropical fruit is often referred to as the "king of fruits" in various Southeast Asian countries.

Durians are known for their large size and thorn-covered husk, which requires careful handling. The flesh inside can vary in color from pale yellow to deep orange, with a custard-like consistency that melts in your mouth. Some describe its taste as a mix of sweet, savory, and creamy, while others find it overpowering and pungent.
"""
    ),
    shinyswatch.theme.minty,
    title="Theme Example",
)

# If __file__ is not defined, use the current working directory
if not globals().get("__file__"):
    __file__ = Path.cwd() / "_purgecss.py"

save_dir = Path(__file__).parent / "output"
if save_dir.exists():
    shutil.rmtree(save_dir)
save_dir.mkdir()
app_ui.save_html(save_dir / "index.html", include_version=False)

purged_dir = Path(__file__).parent / "css"
if purged_dir.exists():
    shutil.rmtree(purged_dir)
purged_dir.mkdir(exist_ok=True)

args = [
    "purgecss",
    "--css",
    "output/lib/shinyswatch-css/bootswatch.min.css",
    "--content",
    "output/index.html",
    "--output",
    "css",
]

subprocess.run(args)

(purged_dir / "bootswatch.min.css").rename(purged_dir / "bootswatch-minty.min.css")

if True:
    shutil.rmtree(save_dir)
