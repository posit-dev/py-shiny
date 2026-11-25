from shiny import App, ui

app_ui = ui.page_fixed(
    # A rule on the textarea itself. An inline `width:100%` beats it; without one,
    # it wins over Bootstrap's `.form-control { width: 100% }`.
    ui.tags.style(".user-width textarea { width: 150px; }"),
    ui.input_text_area("default", "No width"),
    ui.input_text_area("cols", "No width, cols=20", cols=20),
    ui.input_text_area("px", "width=600px", width="600px"),
    ui.input_text_area("px_cols", "width=450px, cols=20", width="450px", cols=20),
    ui.div(
        ui.input_text_area("percent", "width=50%", width="50%"),
        style="width: 800px;",
    ),
    ui.div(
        ui.input_text_area("user_css", "No width, user CSS"),
        class_="user-width",
    ),
    ui.div(
        ui.input_text_area("user_css_px", "width=500px, user CSS", width="500px"),
        class_="user-width",
    ),
)

app = App(app_ui, None)
