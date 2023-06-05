from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from htmltools import HTMLDependency, Tag, tags

from shiny.module import resolve_id

HandOptions = Dict[str, Any]


def dependencies() -> List[HTMLDependency]:
    def subdep(name: str) -> HTMLDependency:
        return HTMLDependency(
            f"@mediapipe/{name}",
            "1.0.0",
            source={
                "package": "shinymediapipe",
                "subdir": f"node_modules/@mediapipe/{name}",
            },
            script=[{"src": f"{name}.js"}],
        )

    return [
        subdep("camera_utils"),
        subdep("control_utils"),
        subdep("drawing_utils"),
        subdep("hands"),
        HTMLDependency(
            "shinymediapipe-hands",
            "1.0.0",
            source={"package": "shinymediapipe", "subdir": ""},
            script={"src": "index.js"},
        ),
    ]


def input_hand(
    id: str,
    options: Optional[HandOptions] = None,
    *,
    debug: bool = False,
    throttle_delay_secs: float = 0.1,
    precision: int = 3,
) -> Tag:
    id = resolve_id(id)
    if options is None:
        options = hand_options()

    return tags.template(
        {
            "id": id,
            "class": "mediapipe-hand-input",
            "data-throttle-delay": throttle_delay_secs * 1000,
            "data-precision": precision,
        },
        {"class": "mediapipe-hand-input-debug"} if debug else None,
        dependencies(),
        tags.script(json.dumps(options), type="application/json"),
    )


# https://google.github.io/mediapipe/solutions/hands.html#configuration-options
def hand_options(
    *,
    maxNumHands: int = 1,
    modelComplexity: float = 1.0,
    minDetectionConfidence: float = 0.9,
    minTrackingConfidence: float = 0.9,
    **kwargs,
) -> HandOptions:
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
