# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Union, cast

from ..types import (
    Coordmap,
    CoordmapDims,
    CoordmapPanel,
    CoordmapPanelDomain,
    CoordmapPanelRange,
)

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.gridspec import SubplotSpec
    from matplotlib.transforms import Transform

# Even though TypedDict is available in Python 3.8, because it's used with NotRequired,
# they should both come from the same typing module.
# https://peps.python.org/pep-0655/#usage-in-python-3-11


def get_coordmap(fig: Figure) -> Union[Coordmap, None]:
    dims_ar: npt.NDArray[np.double] = fig.get_size_inches() * fig.get_dpi()
    dims: CoordmapDims = {
        "width": dims_ar[0],
        "height": dims_ar[1],
    }

    all_axes: List[Axes] = fig.get_axes()  # pyright: reportUnknownMemberType=false

    panels: List[CoordmapPanel] = []
    for i, axes in enumerate(all_axes):
        panel = get_coordmap_panel(axes, i + 1, dims["height"])
        panels.append(panel)

    coordmap: Coordmap = {
        "panels": panels,
        "dims": dims,
    }

    return coordmap


def get_coordmap_panel(axes: Axes, panel_num: int, height: float) -> CoordmapPanel:
    spspec: SubplotSpec = axes.get_subplotspec()

    domain_xlim = cast(Tuple[float, float], axes.get_xlim())
    domain_ylim = cast(Tuple[float, float], axes.get_ylim())

    # Data coordinates of plotting area
    domain: CoordmapPanelDomain = {
        "left": domain_xlim[0],
        "right": domain_xlim[1],
        "bottom": domain_ylim[0],
        "top": domain_ylim[1],
    }

    # Pixel coordinates of plotting area
    transdata: Transform = axes.transData  # pyright: reportGeneralTypeIssues=false

    range_ar: npt.NDArray[np.double] = transdata.transform(
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
        "bottom": height - range_ar[1],
        "top": height - range_ar[3],
    }

    return {
        "panel": panel_num,
        "row": spspec.rowspan.start + 1,  # pyright: reportUnknownVariableType=false
        "col": spspec.colspan.start + 1,  # pyright: reportUnknownVariableType=false
        # "panel_vars": {
        #     "panelvar1": "4",
        #     "panelvar2": "1",
        # },
        "domain": domain,
        "range": range,
        "log": {"x": None, "y": None},
        "mapping": {
            # "x": "wt",
            # "y": "mpg",
            # "panelvar1": "cyl",
            # "panelvar2": "am",
        },
    }
