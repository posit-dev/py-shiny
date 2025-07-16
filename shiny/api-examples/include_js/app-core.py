from pathlib import Path

from shiny import App, ui

js_file = Path(__file__).parent / "js" / "app.js"

app_ui = ui.page_fluid(
    "If you see this page before 'OK'-ing the alert box, something went wrong",
    ui.include_js(js_file),
)


app = App(app_ui, None)
