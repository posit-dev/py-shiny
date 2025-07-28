from shiny.express import input, render, ui

ui.page_opts(title="Slider Parameters Demo", full_width=True)

with ui.layout_column_wrap(width="400px"):
    with ui.card():
        ui.card_header("Basic Numeric Slider")
        ui.input_slider("slider1", "Min, max, value", min=0, max=100, value=50)

        @render.text
        def value1():
            return f"Value: {input.slider1()}"
