import math
from pathlib import Path

from brownian_motion import brownian_data, brownian_widget
from mediapipe import hand_to_camera_eye, xyz_mean
from shinymediapipe import input_hand
from shinywidgets import output_widget, register_widget

from shiny import App, reactive, render, req, ui

# Check that JS prerequisites are installed
if not (Path(__file__).parent / "shinymediapipe" / "node_modules").is_dir():
    raise RuntimeError(
        "Mediapipe dependencies are not installed. "
        "Please run `npm install` in the 'shinymediapipe' subdirectory."
    )

# Set to True to see underlying XYZ values and canvas
debug = True

app_ui = ui.page_fluid(
    ui.input_action_button("data_btn", "New Data"),
    output_widget("plot"),
    input_hand("hand", debug=debug, throttle_delay_secs=0.05),
    (
        ui.panel_fixed(
            ui.div(ui.tags.strong("x:"), ui.output_text("x_debug", inline=True)),
            ui.div(ui.tags.strong("y:"), ui.output_text("y_debug", inline=True)),
            ui.div(ui.tags.strong("z:"), ui.output_text("z_debug", inline=True)),
            ui.div(ui.tags.strong("mag:"), ui.output_text("mag_debug", inline=True)),
            left="12px",
            bottom="12px",
            width="200px",
            height="auto",
            class_="d-flex flex-column justify-content-end",
        )
        if debug
        else None
    ),
    class_="p-3",
)


def server(input, output, session):
    # BROWNIAN MOTION ====

    @reactive.calc
    def random_walk():
        """Generates brownian data whenever 'New Data' is clicked"""
        input.data_btn()
        return brownian_data(n=200)

    # Create Plotly 3D widget and bind it to output_widget("plot")
    widget = brownian_widget(600, 600)
    register_widget("plot", widget)

    @reactive.effect
    def update_plotly_data():
        walk = random_walk()
        layer = widget.data[0]
        layer.x = walk["x"]
        layer.y = walk["y"]
        layer.z = walk["z"]
        layer.marker.color = walk["z"]

    # HAND TRACKING ====

    @reactive.calc
    def camera_eye():
        """The eye position, as reflected by the hand input"""
        hand_val = input.hand()
        req(hand_val)

        res = hand_to_camera_eye(hand_val, detect_ok=True)
        req(res)
        return res

    # The raw data is a little jittery. Smooth it out by averaging a few samples
    smooth_camera_eye = reactive_smooth(n_samples=5, smoother=xyz_mean)(camera_eye)

    @reactive.effect
    def update_plotly_camera():
        """Update Plotly camera using the hand tracking"""
        widget.layout.scene.camera.eye = smooth_camera_eye()

    # DEBUGGING ====

    @render.text
    def x_debug():
        return camera_eye()["x"]

    @render.text
    def y_debug():
        return camera_eye()["y"]

    @render.text
    def z_debug():
        return camera_eye()["z"]

    @render.text
    def mag_debug():
        eye = camera_eye()

        return f"{round(math.sqrt(eye['x']**2 + eye['y']**2 + eye['z']**2), 2)}"


app = App(app_ui, server)


def reactive_smooth(n_samples, smoother, *, filter_none=True):
    """Decorator for smoothing out reactive calculations over multiple samples"""

    def wrapper(calc):
        buffer = []  # Ring buffer of capacity `n_samples`
        result = reactive.value(None)  # Holds the most recent smoothed result

        @reactive.effect
        def _():
            # Get latest value. Because this is happening in a reactive Effect, we'll
            # automatically take a reactive dependency on whatever is happening in the
            # calc().
            new_value = calc()
            buffer.append(new_value)
            while len(buffer) > n_samples:
                buffer.pop(0)

            if not filter_none:
                result.set(smoother(buffer))
            else:
                # The filter cannot handle None values; remove any in the buffer
                filt_samples = [s for s in buffer if s is not None]
                if len(filt_samples) == 0:
                    result.set(None)
                else:
                    result.set(smoother(filt_samples))

        # The return value for the wrapper
        return result.get

    return wrapper
