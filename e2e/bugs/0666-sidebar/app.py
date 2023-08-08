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
        ui.panel_sidebar("`main` - Sidebar content", id="main-sidebar"),
        ui.panel_main("`main` - Main content", id="main-content"),
    ),
    # # Can not use X sidebar as only one htmldependency wins.
    # import shiny.experimental as x
    # x.ui.layout_sidebar(
    #     x.ui.sidebar(
    #         "`x` - Sidebar content",
    #         open="always",
    #         width=f"{int(4 / 12 * 100)}%",
    #         id="x-sidebar",
    #     ),
    #     "`x` - Main content",
    #     id="x-content",
    # ),
)

app = App(app_ui, None)
