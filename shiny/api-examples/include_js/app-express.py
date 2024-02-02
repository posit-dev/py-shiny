from pathlib import Path

from shiny.express import ui

js_file = Path(__file__).parent / "js" / "app.js"

"If you see this page before 'OK'-ing the alert box, something went wrong"

ui.include_js(js_file)
