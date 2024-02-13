from pathlib import Path

from shiny.express import ui

css_file = Path(__file__).parent / "css" / "styles.css"

"Almost before we knew it, we had left the ground!!!"

ui.include_css(css_file)

# Style individual elements with an attribute dictionary.
ui.p("Bold text", {"style": "font-weight: bold"})
