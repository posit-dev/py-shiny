from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="server")

with ui.card():
    ui.card_header("Bookmarking File Input Demo")

    # Non-modular section
    ui.h3("Non-Module Section")

    # Basic file input
    ui.input_file(id="basic", label="Basic file input")

    @render.text
    def basic_text():
        files = input.basic()
        if files is None or len(files) == 0:
            return "No files selected"

        # Extract file names
        file_names = [f["name"] for f in files]
        return f"File name(s): {', '.join(file_names)}"

    # module section

    @module
    def date_module(input, output, session):
        ui.h3("File Input Module")

        # Module file input
        ui.input_file(
            id="module_file",
            label="Module file input",
            multiple=True,
        )

        @render.text
        def mod_text():
            files = input.module_file()
            if files is None or len(files) == 0:
                return "No files selected"

            # Extract file names
            file_names = [f["name"] for f in files]
            return f"File name(s): {', '.join(file_names)}"

    date_module("first")

ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
