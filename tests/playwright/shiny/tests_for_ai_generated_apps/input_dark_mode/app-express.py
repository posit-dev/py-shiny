from shiny.express import input, render, ui

# Add Font Awesome CSS
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">'
    )
)

# Set page options
ui.page_opts(fillable=True)

with ui.layout_sidebar():
    with ui.sidebar():
        ui.input_dark_mode(id="mode", mode="light")

    with ui.card():
        ui.card_header("Dark Mode Example")

        @render.text
        def current_mode():
            return f"Current mode: {input.mode()}"

        ui.p("This is a demonstration of dark mode functionality.")

        with ui.div(class_="mt-3"):
            ui.tags.i(class_="fa-solid fa-moon", style="font-size: 2rem;")
            ui.span(" Dark Mode Toggle Example", class_="ms-2")
