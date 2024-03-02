from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("ui.sidebar() Settings"),
        ui.layout_column_wrap(
            ui.input_select(
                "desktop",
                label="Desktop",
                choices=["open", "closed", "always"],
                selected="open",
            ),
            ui.input_select(
                "mobile",
                label="Mobile",
                choices=["open", "closed", "always"],
                selected="closed",
            ),
            ui.input_select(
                "position", label="Position", choices=["left", "right"], selected="left"
            ),
            width="100px",
        ),
    ),
    ui.layout_column_wrap(
        ui.card(
            ui._card.card_body(
                ui.output_ui("sidebar_dynamic", fill=True, fillable=True), class_="p-0"
            ),
        ),
        ui.card(
            ui.card_header("Sidebar Layout Code"),
            ui.output_code("sidebar_code"),
        ),
        width="500px",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.ui
    def sidebar_dynamic():
        return ui.layout_sidebar(
            ui.sidebar(
                ui.markdown(
                    f"""
                    **Desktop**: {input.desktop()}

                    **Mobile**: {input.mobile()}

                    **Position**: {input.position()}
                    """
                ),
                title="Settings",
                id="sidebar_dynamic",
                open={"desktop": input.desktop(), "mobile": input.mobile()},
                position=input.position(),
            ),
            ui.h2("Dynamic sidebar"),
            ui.output_text_verbatim("state_dynamic"),
        )

    @render.text
    def state_dynamic():
        return f"input.sidebar_dynamic(): {input.sidebar_dynamic()}"

    @render.code
    def sidebar_code():
        if input.desktop() == input.mobile():
            open = f'"{input.desktop()}"'
        elif input.desktop() == "open" and input.mobile() == "closed":
            open = '{"desktop": "open", "mobile": "closed"}'
        else:
            open = f'{{"desktop": "{input.desktop()}", "mobile": "{input.mobile()}}}'

        return f"""\
ui.layout_sidebar(
    ui.sidebar(
        "Sidebar content...",
        title="Sidebar title",
        id="sidebar_id",
        open={open},
        position="{input.position()}"
    ),
    "Main content...",
)
"""


app = App(app_ui, server)
