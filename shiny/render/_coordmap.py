# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Union, cast

from ..types import (
    Coordmap,
    CoordmapDims,
    CoordmapPanel,
    CoordmapPanelDomain,
    CoordmapPanelLog,
    CoordmapPanelRange,
    PlotnineFigure,
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

    log: CoordmapPanelLog = {"x": None, "y": None}
    if axes.axes.xaxis._scale.name == "log":
        log["x"] = axes.xaxis._scale.base
        domain["left"] = axes.xaxis._scale._transform.transform(domain["left"])
        domain["right"] = axes.xaxis._scale._transform.transform(domain["right"])

    if axes.yaxis._scale.name == "log":
        log["y"] = axes.yaxis._scale.base
        domain["top"] = axes.yaxis._scale._transform.transform(domain["top"])
        domain["bottom"] = axes.yaxis._scale._transform.transform(domain["bottom"])

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
        "log": log,
        "mapping": {
            # "x": "wt",
            # "y": "mpg",
            # "panelvar1": "cyl",
            # "panelvar2": "am",
        },
    }


def get_coordmap_plotnine(p: PlotnineFigure, fig: Figure) -> Union[Coordmap, None]:
    coordmap = get_coordmap(fig)

    if coordmap is None:
        return None

    # Plotnine figures handle log scales a bit differently from regular matplotlib
    # Figures. Instead of using log scales in the matplotlib Figure object, it adds log
    # scales in the ggplot object. We need to massage the coordmap at this point to
    # reflect this.
    for scale in p.scales:
        if type(scale._trans).__name__ == "log10_trans":
            if "x" in scale.aesthetics:
                dir_xy = "x"
            elif "y" in scale.aesthetics:
                dir_xy = "y"
            else:
                continue

            # Assume all panels use the same log scale.
            for i in range(len(coordmap["panels"])):
                coordmap["panels"][i]["log"][dir_xy] = scale._trans.base

    return coordmap
