from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url", debug=True)

with ui.card():
    ui.card_header("Bookmarking Password Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Changed from checkbox to password input
    ui.input_password(id="basic", label="Basic password")

    # Added text input for non-module section
    ui.input_text(id="basic_text", label="Basic text input")

    @render.text
    def basic_password_value():
        return f"Password value: {input.basic()}"

    @render.text
    def basic_text_value():
        return f"Text input value: {input.basic_text()}"

    # module section

    @module
    def checkbox_module(input, output, session):
        ui.h3("Password Module")

        # password input
        ui.input_password(id="module_password", label="Basic module password")

        # Added text input for module section
        ui.input_text(id="module_text", label="Module text input")

        @render.text
        def password_text():
            return f"Password value: {input.module_password()}"

        @render.text
        def text_value():
            return f"Text input value: {input.module_text()}"

    checkbox_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
