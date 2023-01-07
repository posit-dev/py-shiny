# Needed for NotRequired with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

import sys
from typing import Dict, List, Union, cast

# Even though TypedDict is available in Python 3.8, because it's used with NotRequired,
# they should both come from the same typing module.
# https://peps.python.org/pep-0655/#usage-in-python-3-11
if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict


class CoordmapDims(TypedDict):
    width: float
    height: float


class CoordmapPanelLog(TypedDict):
    x: Union[bool, None]
    y: Union[bool, None]


class CoordmapPanelDomain(TypedDict):
    left: float
    right: float
    bottom: float
    top: float


class CoordmapPanelRange(TypedDict):
    left: float
    right: float
    bottom: float
    top: float


class CoordmapPanelMapping(TypedDict):
    x: NotRequired[str]
    y: NotRequired[str]


class CoordmapPanel(TypedDict):
    panels: NotRequired[int]
    row: NotRequired[int]
    col: NotRequired[int]
    panel_vars: NotRequired[Dict[str, str]]
    log: CoordmapPanelLog
    domain: CoordmapPanelDomain
    mapping: CoordmapPanelMapping
    range: CoordmapPanelRange


class Coordmap(TypedDict):
    panels: List[CoordmapPanel]
    dims: CoordmapDims


def get_coordmap(figure) -> Union[Coordmap, None]:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    fig = cast(Figure, figure)

    axes: Axes = cast(Axes, fig.get_axes())[0]

    dims_ar = fig.get_size_inches() * fig.get_dpi()
    dims: CoordmapDims = {
        "width": dims_ar[0],
        "height": dims_ar[1],
    }

    domain_xlim = axes.get_xlim()
    domain_ylim = axes.get_ylim()

    # Data coordinates of plotting area
    domain: CoordmapPanelDomain = {
        "left": domain_xlim[0],
        "right": domain_xlim[1],
        "bottom": domain_ylim[0],
        "top": domain_ylim[1],
    }

    # Pixel coordinates of plotting area
    range_ar = axes.transData.transform(
        [
            domain["left"],
            domain["bottom"],
            domain["right"],
            domain["top"],
        ]
    )

    # The values from transData.transform() have origin in the bottom-left, but we need
    # to provide coordinates with origin in upper-left.
    range: CoordmapPanelRange = {
        "left": range_ar[0],
        "right": range_ar[2],
        "bottom": dims["height"] - range_ar[1],
        "top": dims["height"] - range_ar[3],
    }

    coordmap: Coordmap = {
        "panels": [
            {
                "domain": domain,
                "range": range,
                "log": {"x": None, "y": None},
                "mapping": {},
            }
        ],
        "dims": dims,
    }

    return coordmap
