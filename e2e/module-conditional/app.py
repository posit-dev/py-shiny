from shiny import App, Inputs, Outputs, Session, module, ui


def my_ui(message: str) -> ui.TagList:
    return ui.TagList(
        ui.input_checkbox("show", "Show secret message", False),
        ui.panel_conditional(
            "input.show",
            message,
            id=module.resolve_id("cond_message"),
        ),
    )


mod_ui = module.ui(my_ui)


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    ...


app_ui = ui.page_fluid(
    ui.h3("Non-module version"),
    my_ui("Lorem ipsum dolor sit amet"),
    ui.hr(),
    ui.h3("Module version"),
    mod_ui("mod", "consectetur adipiscing elit"),
)


def server(input: Inputs, output: Outputs, session: Session):
    mod_server("mod")


app = App(app_ui, server)
