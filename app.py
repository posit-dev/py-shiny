from shiny.express import input, render, ui

ui.input_date("date", "Date")

@render.text
def value():
    return input.date()
