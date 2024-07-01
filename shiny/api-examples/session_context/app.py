from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny.session import session_context


# ============================================================
# Slider module
# ============================================================
@module.ui
def slider_ui(label: str = "Slider", value: int = 0) -> ui.TagChild:
    return ui.card(
        ui.input_slider(id="slider", label=label, min=0, max=5, value=value),
        ui.output_text_verbatim(id="out"),
    )


@module.server
def slider_server(
    input: Inputs,
    # Include `output`, `session` so that we can return `session`
    output: Outputs,
    session: Session,
) -> Session:
    @render.text
    def out() -> str:
        return f"Module - input.slider(): {input.slider()}"

    # Return module's session
    return session


# =============================================================================
# App that uses module
# =============================================================================
app_ui = ui.page_fluid(
    ui.markdown(
        "# Use `session_context(session)` to manually set the session value within a context"
    ),
    ui.br(),
    ui.input_action_button(id="reset_sliders", label="Reset sliders to 0"),
    ui.br(),
    ui.br(),
    slider_ui("slider1", "Module: Slider 1", 2),
    slider_ui("slider2", "Module: Slider 2", 5),
)


def server(input: Inputs):
    slider1_session = slider_server("slider1")
    slider2_session = slider_server("slider2")

    @reactive.Effect
    @reactive.event(input.reset_sliders)
    def _():
        # Update each slider within its module's session
        with session_context(slider1_session):
            ui.update_slider("slider", value=0)
        with session_context(slider2_session):
            ui.update_slider("slider", value=0)


app = App(app_ui, server)
