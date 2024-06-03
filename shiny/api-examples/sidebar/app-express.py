from shiny.express import input, render, ui

ui.page_opts(fillable=True)

with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(id="sidebar_left", open="desktop"):
            "Left sidebar content"

        @render.code
        def state_left():
            return f"input.sidebar_left(): {input.sidebar_left()}"


with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(id="sidebar_right", position="right", open="desktop"):
            "Right sidebar content"

        @render.code
        def state_right():
            return f"input.sidebar_right(): {input.sidebar_right()}"


with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(id="sidebar_closed", open="closed"):
            "Closed sidebar content"

        @render.code
        def state_closed():
            return f"input.sidebar_closed(): {input.sidebar_closed()}"


with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(id="sidebar_always", open="always"):
            "Always sidebar content"

        @render.code
        def state_always():
            return f"input.sidebar_always(): {input.sidebar_always()}"
