import math
from functools import reduce
from operator import add
from statistics import mean

import numpy as np

WRIST = 0
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4
INDEX_FINGER_MCP = 5
INDEX_FINGER_PIP = 6
INDEX_FINGER_DIP = 7
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_MCP = 9
MIDDLE_FINGER_PIP = 10
MIDDLE_FINGER_DIP = 11
MIDDLE_FINGER_TIP = 12
RING_FINGER_MCP = 13
RING_FINGER_PIP = 14
RING_FINGER_DIP = 15
RING_FINGER_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20


def hand_to_camera_eye(hands, detect_ok=False):
    # TODO: Pointing straight at the camera should not change (much) from the default
    # position
    # TODO: Use spherical coordinates instead of cartesian

    left_hand = hands["multiHandedness"][0]["index"] == 0
    hand = hands["multiHandLandmarks"][0]

    def rel_hand(start_pos: int, end_pos: int):
        return np.subtract(list(hand[start_pos].values()), list(hand[end_pos].values()))

    if detect_ok:
        # If the distance between the thumbtip and index finger tip are pretty close,
        # ignore the hand. (Using "OK" sign to pause hand tracking)
        ok_dist = np.linalg.norm(rel_hand(THUMB_TIP, INDEX_FINGER_TIP))
        ref_dist = np.linalg.norm(rel_hand(INDEX_FINGER_TIP, INDEX_FINGER_DIP))
        if ok_dist < ref_dist * 2:
            return None

    if not left_hand:
        normal_vec = np.cross(
            rel_hand(PINKY_MCP, WRIST),
            rel_hand(INDEX_FINGER_MCP, WRIST),
        )
    else:
        normal_vec = np.cross(
            rel_hand(INDEX_FINGER_MCP, WRIST),
            rel_hand(PINKY_MCP, WRIST),
        )
    normal_unit_vec = normal_vec / np.linalg.norm(normal_vec)

    def list_to_xyz(x):
        x = list(map(lambda y: round(y, 2), x))
        return dict(x=x[0], y=x[1], z=x[2])

    # Invert, for some reason
    normal_unit_vec = normal_unit_vec * -1.0
    normal_unit_vec[1] *= 2.0

    # Stay a consistent distance from the origin
    dist = 2
    magnitude = math.sqrt(reduce(add, [a**2 for a in normal_unit_vec]))
    normal_unit_vec = [a / magnitude * dist for a in normal_unit_vec]

    new_eye = list_to_xyz(normal_unit_vec)
    return {
        # Adjust locations to match camera position
        "x": new_eye["z"],
        "y": new_eye["x"],
        "z": new_eye["y"],
    }


def xyz_mean(points):
    return dict(
        x=mean([p["x"] for p in points]),
        y=mean([p["y"] for p in points]),
        z=mean([p["z"] for p in points]),
    )
