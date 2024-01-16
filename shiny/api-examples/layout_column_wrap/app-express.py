import shiny
from shiny.express import ui

a_card = shiny.ui.card("A simple card")

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
