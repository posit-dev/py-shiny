import numpy as np
from shiny import ui
import json


def mediapipe_ui(
    name,
    *,
    videoId="video",
    canvasId="canvas",
    options=None,
    debug=True,
):

    assert type(name) is str
    assert type(videoId) is str
    assert type(canvasId) is str
    assert type(debug) is bool

    if options is None:
        options = hand_options()
    mediapipHandArgs = {
        "uiName": name,
        "videoId": videoId,
        "canvasId": canvasId,
        "options": options,
        "debug": debug,
    }
    mediapipe_js = f"mediapipeHand({json.dumps(mediapipHandArgs)})"

    if debug:
        canvasStyle = "display:block;"
    else:
        canvasStyle = "display:none;"

    return ui.TagList(
        ui.tags.video(id=videoId, style="display:none;"),
        ui.tags.canvas(id=canvasId, style=canvasStyle),
        ui.tags.script(
            src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js",
            crossorigin="anonymous",
        ),
        ui.tags.script(
            src="https://cdn.jsdelivr.net/npm/@mediapipe/control_utils/control_utils.js",
            crossorigin="anonymous",
        ),
        ui.tags.script(
            src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js",
            crossorigin="anonymous",
        ),
        ui.tags.script(
            src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js",
            crossorigin="anonymous",
        ),
        ui.tags.script(src="hand.js"),
        ui.tags.script(mediapipe_js),
    )


# https://google.github.io/mediapipe/solutions/hands.html#configuration-options
def hand_options(
    *,
    maxNumHands: int = 1,
    modelComplexity: float = 1.0,
    minDetectionConfidence: float = 0.9,
    minTrackingConfidence: float = 0.9,
    **kwargs,
):
    maxNumHands = int(maxNumHands)
    modelComplexity = float(modelComplexity)
    minDetectionConfidence = float(minDetectionConfidence)
    minTrackingConfidence = float(minTrackingConfidence)
    assert 0 < maxNumHands
    assert 0 <= modelComplexity <= 1
    assert 0 <= minDetectionConfidence <= 1
    assert 0 <= minTrackingConfidence <= 1

    return {
        "staticImageMode": False,
        "maxNumHands": maxNumHands,
        "modelComplexity": modelComplexity,
        "minDetectionConfidence": minDetectionConfidence,
        "minTrackingConfidence": minTrackingConfidence,
        # Future model expansion
        **kwargs,
    }


def hand_to_camera_eye(hand):
    def rel_hand(start_pos: int, end_pos: int):
        return np.subtract(list(hand[start_pos].values()), list(hand[end_pos].values()))

    normal_vec = np.cross(rel_hand(17, 0), rel_hand(5, 0))
    normal_unit_vec = normal_vec / np.linalg.norm(normal_vec)

    def list_to_xyz(x):
        x = list(map(lambda y: round(y, 2), x))
        return dict(x=x[0], y=x[1], z=x[2])

    # Make zoom bigger and invert
    new_eye = list_to_xyz(normal_unit_vec * 2.0 * -1.0)
    return {
        # Adjust locations to match camera position
        "x": new_eye["z"],
        "y": new_eye["x"],
        "z": new_eye["y"] * 2.0,
    }
