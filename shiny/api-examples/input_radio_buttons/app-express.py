from shiny.express import input, render, ui

ui.input_radio_buttons(
    "rb",
    "Choose one:",
    {
        "html": ui.HTML("<span style='color:red;'>Red Text</span>"),
        "text": "Normal text",
    },
)


@render.express
def val():
    "You chose " + input.rb()
