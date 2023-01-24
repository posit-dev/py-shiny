from typing import Union

from ..types import (
    Coordmap,
    CoordmapDims,
    CoordmapPanelDomain,
    CoordmapPanelRange,
    MplAxes,
    MplFigure,
)

# Even though TypedDict is available in Python 3.8, because it's used with NotRequired,
# they should both come from the same typing module.
# https://peps.python.org/pep-0655/#usage-in-python-3-11


def get_coordmap(fig: MplFigure) -> Union[Coordmap, None]:
    axes: MplAxes = fig.get_axes()[0]

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
