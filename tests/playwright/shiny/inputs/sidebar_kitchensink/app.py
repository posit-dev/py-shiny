from shiny.express import input, render, ui

ui.page_opts(fillable=True)

with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(
            id="sidebar_left",
            open="desktop",
            title="Left sidebar",
            bg="dodgerBlue",
            class_="text-white",
            gap="20px",
            padding="10px",
            width="200px",
        ):
            "Left sidebar content"

        @render.code
        def state_left():
            return f"input.sidebar_left(): {input.sidebar_left()}"


with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(
            id="sidebar_right",
            position="right",
            open={"desktop": "closed", "mobile": "open"},
            padding=["10px", "20px"],
            bg="SlateBlue",
        ):
            "Right sidebar content"

        @render.code
        def state_right():
            return f"input.sidebar_right(): {input.sidebar_right()}"


with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(
            id="sidebar_closed",
            open="closed",
            bg="LightCoral",
            padding=["10px", "20px", "30px"],
        ):
            "Closed sidebar content"

        @render.code
        def state_closed():
            return f"input.sidebar_closed(): {input.sidebar_closed()}"


with ui.card():
    with ui.layout_sidebar():
        with ui.sidebar(
            id="sidebar_always",
            open="always",
            bg="PeachPuff",
            padding=["10px", "20px", "30px", "40px"],
            max_height_mobile="175px",
        ):
            "Always sidebar content"

        @render.code
        def state_always():
            return f"input.sidebar_always(): {input.sidebar_always()}"
