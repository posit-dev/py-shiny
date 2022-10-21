from pathlib import Path
import numpy as np
import plotly.express as px
import ipywebrtc
import io
import PIL.Image

# multi-variate projection, connect fingers to each dimension, should be small amount of code
# Move projection code to imported file


from shiny import *
from shinywidgets import output_widget, reactive_read, register_widget
import plotly.graph_objs as go

app_ui = ui.page_fluid(
    output_widget("camera"),
    # ui.tags.video(id="video", style="display:block;"),
    ui.tags.video(id="video", style="display:none;"),
    ui.tags.canvas(id="canvas", style="display:block;"),
    # ui.tags.canvas(id="canvas", style="display:none;"),
    ui.output_text_verbatim("eye", placeholder=True),
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
    ui.tags.script(src="image.js"),
    output_widget(
        "threeD",
        height="600px",
    ),
)


def server(input, output, session):

    color_switch = {
        "setosa": "red",
        "versicolor": "green",
        "virginica": "blue",
    }
    iris = px.data.iris()
    iris_color = iris.species.map(color_switch)
    threeD = go.FigureWidget(
        data=[
            go.Scatter3d(
                x=iris.sepal_length,
                y=iris.sepal_width,
                z=iris.petal_length,
                mode="markers",
                marker=dict(
                    symbol="circle",
                    size=3,
                    color=iris_color,
                ),
                # hover_data=iris.petal_width,
            ),
        ],
        layout={"showlegend": True},
    )

    register_widget("threeD", threeD)

    # @reactive.Effect
    # async def _():
    #     req(False)
    #     hand = input.hand()
    #     req(hand)
    #     # await session.send_custom_message("eye", hand[8])
    #     # threeD.update_layout()
    #     def finger_distance(tip, base):
    #         return (
    #             abs(tip["x"] - base["x"])
    #             + abs(tip["y"] - base["y"])
    #             + abs(tip["z"] - base["z"])
    #         )

    #     eye = {
    #         "x": finger_distance(hand[8], hand[5]),
    #         "y": finger_distance(hand[12], hand[9]),
    #         "z": finger_distance(hand[16], hand[13]),
    #     }
    #     eye_total = max([eye["x"], eye["y"], eye["z"]])
    #     eye["x"] = eye["x"] / eye_total
    #     eye["y"] = eye["y"] / eye_total
    #     eye["z"] = eye["z"] / eye_total
    #     print(eye)

    #     threeD.layout.scene.camera.eye = eye

    @reactive.Calc
    def hand():
        # Throttle the hand value to 10Hz
        reactive.invalidate_later(0.1)
        with reactive.isolate():
            hand_val = input.hand()
        req(hand_val)
        return hand_val

    @reactive.Calc
    async def hand_info():
        hand_val = hand()

        # def p_norm = lambda x, p: np.power(np.sum(np.power(np.abs(x), p)), 1/p)
        # def norm_1 = lambda x: p_norm(x, 1)
        # def norm_2 = lambda x: p_norm(x, 2)
        def vec(x):
            return list(x.values())

        def vec_sub(x, y):
            return np.subtract(vec(x), vec(y))

        u = vec_sub(hand_val[5], hand_val[0])
        v = vec_sub(hand_val[17], hand_val[0])
        normal_vec = np.cross(v, u)
        normal_unit_vec = normal_vec / np.linalg.norm(normal_vec)

        def list_to_xyz(x):
            x = list(map(lambda y: round(y, 2), x))
            return dict(x=x[0], y=x[1], z=x[2])

        # Make zoom bigger
        # cur_eye = {
        #     "x": threeD.layout.scene.camera.eye["x"],
        #     "y": threeD.layout.scene.camera.eye["y"],
        #     "z": threeD.layout.scene.camera.eye["z"],
        # }
        # cur_eye_mag = np.linalg.norm(list(cur_eye.values()))
        # new_eye = list_to_xyz(normal_vec * -1.0 * 2.5 * 100)
        new_eye = list_to_xyz(normal_unit_vec * 2.5 * -1.0)
        # x,y,z - off
        # y,x,z - off
        # x,z,y - close!; sidways rotations were backwards
        # y,z,x - off
        # z,x,y - good; vertical was backwards; maybe up param?
        # z,y,x - off
        new_eye_dict = {
            "x": new_eye["z"],
            "y": new_eye["x"],
            "z": new_eye["y"] * 2.0,
        }
        return {
            # "eye": cur_eye,
            "norm_unit_vec": normal_unit_vec,
            "new_eye": new_eye_dict,
        }

    @reactive.Effect
    async def _():
        hand_info_ = await hand_info()
        threeD.layout.scene.camera.eye = hand_info_["new_eye"]

    @output
    @render.text
    async def eye():
        eye = (await hand_info())["new_eye"]
        return f"x: {eye['x']}, y: {eye['y']}, z: {eye['z']}"

    # camera = ipywebrtc.CameraStream(
    #     constraints={
    #         "facing_mode": "user",
    #         "audio": False,
    #         "video": {"width": 640, "height": 480},
    #     }
    # )
    # image_recorder = ipywebrtc.ImageRecorder(stream=camera)
    # image_recorder.recording = True
    # register_widget("camera", camera)

    # @reactive.Effect
    # def _():
    #     reactive.invalidate_later(1)

    #     try:
    #         im = PIL.Image.open(io.BytesIO(image_recorder.image.value))
    #         im_array = np.array(im)
    #         print(im_array)
    #     except Exception as e:
    #         print("Error received")
    #         print(e)
    #     # image = reactive_read(image_recorder.image, "value")
    #     # print(image)
    #     # print(image.value)


# for multivariant, maybe set `up.z` to `1`?

www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)
