from shiny.express import input, render, ui

ui.input_text("name", "Name", "Socrates")
ui.input_text("years", "Years", "470-399 BC")


@render.express
def person():
    with ui.card(class_="mt-3"):
        ui.h3(input.name())
        input.years()
