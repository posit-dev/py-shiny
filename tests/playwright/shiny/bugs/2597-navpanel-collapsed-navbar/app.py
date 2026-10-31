"""
Regression app for #2597.

`ui.page_navbar()` collapses its tabs behind a toggler button below 768px wide.
`controller.NavPanel.click()` opened a closed dropdown before clicking a tab in
it, but not a collapsed navbar, so clicking a tab in a narrow window failed.
"""

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_navbar(
    ui.nav_panel("A", "Panel A content"),
    ui.nav_panel("B", "Panel B content"),
    ui.nav_menu("More", ui.nav_panel("C", "Panel C content")),
    id="navbar",
    title="Collapsed navbar",
    footer=ui.output_text("selected"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def selected():
        return f"Selected: {input.navbar()}"


app = App(app_ui, server)
