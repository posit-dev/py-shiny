from shiny.express import ui

with ui.hold() as a_card:
    with ui.card():
        "A simple card"

# Always has 2 columns (on non-mobile)
with ui.layout_column_wrap(width=1 / 2):
    a_card
    a_card
    a_card

ui.hr()

# Has three columns when viewport is wider than 750px
with ui.layout_column_wrap(width="250px"):
    a_card
    a_card
    a_card
