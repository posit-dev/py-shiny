from shiny.express import ui

with ui.card(full_screen=True):
    ui.card_header("This is the header")
    ui.p("This is the body.")
    ui.p("This is still the body.")
    ui.card_footer("This is the footer")
