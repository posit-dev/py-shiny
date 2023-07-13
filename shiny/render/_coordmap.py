# pyright: reportUnknownMemberType=false

# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any, cast

from ..types import (
    Coordmap,
    CoordmapDims,
    CoordmapPanel,
    CoordmapPanelDomain,
    CoordmapPanelLog,
    CoordmapPanelMapping,
    CoordmapPanelRange,
    PlotnineFigure,
)

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.gridspec import SubplotSpec


def get_coordmap(fig: Figure) -> Coordmap | None:
    dims_ar = fig.get_size_inches() * fig.get_dpi()
    dims: CoordmapDims = {
        "width": dims_ar[0],
        "height": dims_ar[1],
    }

    all_axes = cast(
        "list[Axes]",  # pyright: ignore
        fig.get_axes(),
    )

    panels: list[CoordmapPanel] = []
    for i, axes in enumerate(all_axes):
        panel = get_coordmap_panel(axes, i + 1, dims["height"])
        panels.append(panel)

    coordmap: Coordmap = {
        "panels": panels,
        "dims": dims,
    }

    return coordmap


def get_coordmap_panel(axes: Axes, panel_num: int, height: float) -> CoordmapPanel:
    spspec = cast(
        "SubplotSpec",
        axes.get_subplotspec(),  # pyright: ignore[reportGeneralTypeIssues]
    )

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
    transdata = axes.transData

    range_ar = cast(
        "npt.NDArray[np.double]",
        transdata.transform(
            [
                domain["left"],
                domain["bottom"],
                domain["right"],
                domain["top"],
            ]
        ),
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
    xaxis: Any = axes.xaxis  # pyright: ignore[reportGeneralTypeIssues]
    if xaxis._scale.name == "log":
        log["x"] = xaxis._scale.base
        domain["left"] = xaxis._scale._transform.transform(domain["left"])
        domain["right"] = xaxis._scale._transform.transform(domain["right"])

    yaxis: Any = axes.yaxis  # pyright: ignore[reportGeneralTypeIssues]
    if yaxis._scale.name == "log":
        log["y"] = yaxis._scale.base
        domain["top"] = yaxis._scale._transform.transform(domain["top"])
        domain["bottom"] = yaxis._scale._transform.transform(domain["bottom"])

    return {
        "panel": panel_num,
        "row": spspec.rowspan.start + 1,
        "col": spspec.colspan.start + 1,
        # "panel_vars": {
        #     "panelvar1": "4",
        #     "panelvar2": "1",
        # },
        "domain": domain,
        "range": range,
        "log": log,
        "mapping": {
            "x": None,
            "y": None,
            # "x": "wt",
            # "y": "mpg",
            # "panelvar1": "cyl",
            # "panelvar2": "am",
        },
    }


def get_coordmap_plotnine(p: PlotnineFigure, fig: Figure) -> Coordmap | None:
    coordmap = get_coordmap(fig)

    if coordmap is None:
        return None

    p = deepcopy(p)
    p._build()  # pyright: ignore[reportGeneralTypeIssues]

    # Plotnine/ggplot figures can contain some information that is not in the matplotlib
    # Figure object that is generated.

    # The mappings are shared across all panels, so just get them once.
    mappings = _get_mappings(p)

    for i in range(len(coordmap["panels"])):
        # Copy the panel object; we'll mutate it, and then assign the copy back.
        panel = deepcopy(coordmap["panels"][i])
        panel_num = panel["panel"]

        panel["mapping"] = mappings.copy()

        # Slice out the row of the layout data frame that corresponds to this panel.
        layout_row = p.layout.layout.loc[p.layout.layout["PANEL"] == panel_num]

        # Get values of panelvars
        if "panelvar1" in panel["mapping"]:
            panel["panel_vars"] = {}
            panelvar1 = panel["mapping"]["panelvar1"]  # pyright: ignore
            # If panelvar1 is, say, "cyl", then panelvar1_val will be something like 4.
            panelvar1_val = _simplify_type(layout_row[panelvar1].iloc[0])
            panel["panel_vars"]["panelvar1"] = panelvar1_val  # pyright: ignore

        if "panelvar2" in panel["mapping"]:
            panelvar2 = panel["mapping"]["panelvar2"]  # pyright: ignore
            panelvar2_val = _simplify_type(layout_row[panelvar2].iloc[0])
            panel["panel_vars"]["panelvar2"] = panelvar2_val  # pyright: ignore

        # Get x and y scales
        xscale_num = layout_row["SCALE_X"].iloc[0]
        yscale_num = layout_row["SCALE_Y"].iloc[0]
        xscale = p.layout.panel_scales_x[xscale_num - 1]
        yscale = p.layout.panel_scales_y[yscale_num - 1]

        # Plotnine objects handle log scales a bit differently from regular matplotlib
        # Figures. Instead of using log scales in the matplotlib Figure object, it adds
        # log scales in the ggplot object.
        if hasattr(xscale, "_trans") and _is_log_trans(xscale._trans):
            panel["log"]["x"] = xscale._trans.base
        if hasattr(yscale, "_trans") and _is_log_trans(yscale._trans):
            panel["log"]["y"] = yscale._trans.base

        if hasattr(xscale, "_trans") and _is_reverse_trans(xscale._trans):
            domain = panel["domain"]
            panel["domain"]["left"] = -domain["left"]
            panel["domain"]["right"] = -domain["right"]
        if hasattr(yscale, "_trans") and _is_reverse_trans(yscale._trans):
            domain = panel["domain"]
            panel["domain"]["top"] = -domain["top"]
            panel["domain"]["bottom"] = -domain["bottom"]

        # Plotnine figures can also have transforms in the coordinates. We will assume
        # that log coord transforms are not used along with log scales, because that
        # would be really strange.
        if hasattr(p.layout.coord, "trans_x") and _is_log_trans(p.layout.coord.trans_x):
            panel["log"]["x"] = p.layout.coord.trans_x.base
        if hasattr(p.layout.coord, "trans_y") and _is_log_trans(p.layout.coord.trans_y):
            panel["log"]["y"] = p.layout.coord.trans_y.base

        # Assign temporary panel object back to coordmap.
        coordmap["panels"][i] = panel

    return coordmap


# Given a Plotnine transform object, report whether it is a log transform.
def _is_log_trans(trans: object) -> bool:
    return bool(re.fullmatch("log.*_trans", type(trans).__name__))


# Given a Plotnine transform object, report whether it is a reverse transform.
def _is_reverse_trans(trans: object) -> bool:
    return type(trans).__name__ == "reverse_trans"


def _get_mappings(p: PlotnineFigure) -> CoordmapPanelMapping:
    mapping: CoordmapPanelMapping = {"x": None, "y": None}

    if "x" in p.mapping:
        mapping["x"] = p.mapping["x"]
    if "y" in p.mapping:
        mapping["y"] = p.mapping["y"]

    if type(p.layout.coord).__name__ == "coord_flip":
        (mapping["x"], mapping["y"]) = (mapping["y"], mapping["x"])

    # The names (not values) of panel vars are the same across all panels.
    if type(p.layout.facet).__name__ == "facet_grid":
        n = 1
        if len(p.layout.facet.cols) > 0:
            mapping[f"panelvar{n}"] = p.layout.facet.cols[0]
            n += 1
        if len(p.layout.facet.rows) > 0:
            mapping[f"panelvar{n}"] = p.layout.facet.rows[0]

    elif type(p.layout.facet).__name__ == "facet_wrap":
        mapping["panelvar1"] = p.layout.facet.vars[0]

    return mapping


# Sometimes columns are types that are not JSON serializable, like np.int64. Convert
# these to types that are JSON serializable.
def _simplify_type(x: Any) -> Any:
    import numpy as np

    if isinstance(x, np.integer):
        return int(x)  # pyright: ignore[reportUnknownArgumentType]
    elif isinstance(x, np.floating):
        return float(x)  # pyright: ignore[reportUnknownArgumentType]
    else:
        return x
