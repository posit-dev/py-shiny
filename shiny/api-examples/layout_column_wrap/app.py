from shiny import App, ui

y = ui.card("A simple card")

app_ui = ui.page_fluid(
    # Always has 2 columns (on non-mobile)
    ui.layout_column_wrap(1 / 2, y, y, y),
    ui.hr(),
    # Has three columns when viewport is wider than 750px
    ui.layout_column_wrap("250px", y, y, y),
)


app = App(app_ui, server=None)
