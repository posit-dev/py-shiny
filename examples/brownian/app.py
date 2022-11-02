from pathlib import Path

from brownian_motion import brownian_data, brownian_ui, brownian_widget
from mediapipe import hand_to_camera_eye, mediapipe_ui

from shiny import App, reactive, render, req, ui

debug = False

app_ui = ui.page_fluid(
    ui.h1("Rotate plot using hand tracking"),
    mediapipe_ui("hand", debug=debug),
    ui.output_text_verbatim("eye", placeholder=True) if debug else None,
    brownian_ui("plot"),
    ui.input_action_button("data_btn", "New Data"),
)


def server(input, output, session):

    # TODO-make a reactive calc
    random_walk = brownian_data(n=200)

    widget = brownian_widget("plot", random_walk)

    hand = reactive.Value(0)

    @reactive.Effect
    def _():
        req(input.data_btn())

        data = brownian_data(n=200)
        layer = widget.data[0]
        layer.x = data["x"]
        layer.y = data["y"]
        layer.z = data["z"]

    @reactive.Effect
    def _():
        # Throttle the hand value to 10Hz
        reactive.invalidate_later(0.1)
        with reactive.isolate():
            hand.set(input.hand())

    @reactive.Calc
    def camera_eye():
        hand_val = hand()
        req(hand_val)

        return hand_to_camera_eye(hand_val)

    @reactive.Effect
    def _():
        widget.layout.scene.camera.eye = camera_eye()

    if debug:

        @output
        @render.text
        def eye():
            eye = camera_eye()
            return f"x: {eye['x']}, y: {eye['y']}, z: {eye['z']}"


www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)
