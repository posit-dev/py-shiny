from colors import bg_color, fg_color

from shiny import App, ui

app_ui = ui.page_fluid(
    ui.tags.style(
        f"""
        :root .bslib-sidebar-layout {{
            --bslib-sidebar-bg: {bg_color};
            --bslib-sidebar-fg: {fg_color};
        }}
        """
    ),
    ui.layout_sidebar(
        ui.panel_sidebar("Sidebar content - 1", id="s1"),
        ui.panel_main("Main content - 1", id="m1"),
    ),
    ui.layout_sidebar(
        ui.panel_sidebar("Sidebar content - 2", id="s2"),
        ui.panel_main("Main content - 2", id="m2"),
        "right",
    ),
    ui.layout_sidebar(
        ui.sidebar("Sidebar content - 3", id="s3"),
        "Main content - 3",
        id="m3",
    ),
    ui.layout_sidebar(
        ui.sidebar("Sidebar content - 4", id="s4", position="right"),
        "Main content - 4",
        id="m4",
    ),
)

app = App(app_ui, None)
