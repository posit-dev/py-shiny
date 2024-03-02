from shiny.express import input, output_args, render, ui

ui.input_text("txt", "Enter the text to display below:", "delete me")

with ui.card():
    ui.card_header(ui.code("ui.render_text"))

    @render.text
    def text1():
        return input.txt()


with ui.card():
    ui.card_header(ui.code("@output_args(placeholder=True)"))

    @output_args(placeholder=True)
    @render.code
    def text2():
        return input.txt()


with ui.card():
    ui.card_header(ui.code("@output_args(placeholder=False)"))

    @output_args(placeholder=False)
    @render.code
    def text3():
        return input.txt()
