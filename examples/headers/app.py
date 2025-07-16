from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.h3("HTTP request headers"),
    ui.output_code("headers", placeholder=True),
    ui.h3("User and groups"),
    ui.output_code("user_groups", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.code
    def headers():
        s = ""
        for key, value in session.http_conn.headers.items():
            s += f"{key}: {value}\n"

        return s

    @render.code
    def user_groups():
        return f"session.user: {session.user}\nsession.groups: {session.groups}"


app = App(app_ui, server)
