from shiny.shinyapp import ShinyApp
from shiny import *
from htmltools import *

ui = page_fluid(
    input_slider("slider", "input_slider()", 0, 100, 50),
    input_date("date", "input_date()"),
    input_date_range("date_range", "input_date_range()"),
    input_text("txt", "input_text()", placeholder="Input some text"),
    input_text_area("txt_area", "input_text_area()",
                    placeholder="Input some text"),
    input_button("btn", "input_button()"),
    input_link("link", "input_link()"),
    input_checkbox("checkbox", "input_checkbox()"),
    input_checkbox_group(
        "checkbox_group", "input_checkbox_group()",
        {"Choice 1": "a", "Choice 2": "b"},
        selected="b", inline=True
    ),
    input_radio_buttons(
        "radio", "input_radio()",
        {"Choice 1": "a", "Choice 2": "b"}
    )
    #input_select("select", "input_select()", "Select me"),
)

def server(input, output):
  pass

app = ShinyApp(ui, server)

if __name__ == "__main__":
  app.run()
