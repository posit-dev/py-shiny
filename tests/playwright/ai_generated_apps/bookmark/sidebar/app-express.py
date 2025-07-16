from shiny.express import app_opts, input, module, render, session, ui

app_opts(bookmark_store="url")

with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(id="sidebar_left", open="open", bg="#f74f7a"):
            "Left sidebar content"

        @render.text
        def state_left():
            return f"input.sidebar_left(): {input.sidebar_left()}"

    # Module section in sidebar
    @module
    def sidebar_module(input, output, session):
        with ui.layout_sidebar():
            with ui.sidebar(
                id="sidebar_right", position="right", open="open", bg="#4fa3f7"
            ):
                "Right sidebar content"

            @render.text
            def state_right():
                return f"input.sidebar_right(): {input.sidebar_right()}"

    sidebar_module("first")

    ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
