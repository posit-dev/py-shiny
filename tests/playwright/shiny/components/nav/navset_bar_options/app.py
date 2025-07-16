from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Page 1",
        ui.navset_bar(
            ui.nav_panel("Inner 1", "Inner content"),
            title="Inner navbar",
            id="inner_navset_bar",
            navbar_options=ui.navbar_options(class_="bg-light", theme="light"),
        ),
    ),
    title="Title",
    id="page_navbar",
    navbar_options=ui.navbar_options(class_="bg-primary", theme="dark"),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
