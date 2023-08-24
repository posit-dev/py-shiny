import textwrap

from shiny import App, Inputs, Outputs, Session
from shiny import experimental as x
from shiny import module, render, ui


# ============================================================
# Counter module
# ============================================================
@module.ui
def mod_x_ui(label: str) -> ui.TagChild:
    return ui.div(
        x.ui.layout_sidebar(
            x.ui.sidebar("Sidebar content", id="sidebar"),
            ui.h2(label),
            x.ui.accordion(
                x.ui.accordion_panel("Panel 1", "Content 1"),
                x.ui.accordion_panel("Panel 2", "Content 2"),
                id="accordion",
            ),
            x.ui.popover(
                ui.input_action_button("popover_btn", "Popover btn"),
                "Popover content",
                id="popover",
            ),
            x.ui.tooltip(
                ui.input_action_button("tooltip_btn", "Tooltip btn"),
                "Tooltip content",
                id="tooltip",
            ),
            ui.output_text_verbatim("out", placeholder=True),
        ),
    )


@module.server
def mod_x_server(
    input: Inputs,
    output: Outputs,
    session: Session,
):
    # ## Debug
    # from shiny import reactive
    # @reactive.Effect
    # def _():
    #     print(
    #         [
    #             key
    #             for key in input._map.keys()
    #             if not key.startswith(".") and not key.startswith("mod")
    #         ]
    #     )
    #     print(input._ns)

    @output
    @render.text
    def out():
        return textwrap.dedent(
            f"""
            sidebar: {input.sidebar()}
            accordion: {input.accordion()}
            popover: {input.popover()}
            tooltip: {input.tooltip()}
            """
        ).strip()


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    mod_x_ui("mod1", "Module 1"),
    mod_x_ui("mod2", "Module 2"),
    ui.h3("Inputs that are not in a module:"),
    ui.output_text_verbatim("not_modules", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    mod_x_server("mod1")
    mod_x_server("mod2")

    @output
    @render.text
    def not_modules():
        bad_keys: list[str] = []
        for key in input._map.keys():
            if key.startswith(".") or key.startswith("mod"):
                continue
            bad_keys.append(key)
        return str(bad_keys)


app = App(app_ui, server)
