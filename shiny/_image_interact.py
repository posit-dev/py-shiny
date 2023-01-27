# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Optional, Union

# Even though TypedDict is available in Python 3.8, because it's used with NotRequired,
# they should both come from the same typing module.
# https://peps.python.org/pep-0655/#usage-in-python-3-11
if sys.version_info >= (3, 11):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from .types import BrushInfo, CoordInfo, CoordXY

if TYPE_CHECKING:
    import numpy.typing as npt
    import pandas as pd


class SeriesXY(TypedDict):
    x: pd.Series[float]
    y: pd.Series[float]


def brushed_points(
    df: pd.DataFrame,
    brush: Union[BrushInfo, None],
    xvar: Optional[str] = None,
    yvar: Optional[str] = None,
    *,
    all_rows: bool = False,
) -> pd.DataFrame:
    import pandas as pd

    new_df = df.copy()

    if brush is None:
        if all_rows:
            new_df["selected_"] = False
        else:
            new_df = new_df.loc[[]]

        return new_df

    if "xmin" not in brush:
        raise ValueError(
            "brushedPoints requires a brush object with xmin, xmax, ymin, and ymax."
        )

    # Which direction(s) the brush is selecting over. Direction can be 'x', 'y',
    # or 'xy'.
    use_x = "x" in brush["direction"]
    use_y = "y" in brush["direction"]

    # TODO: Try to extract vars from brush object

    # Filter out x and y values
    keep_rows: pd.Series[bool] = pd.Series(True, index=new_df.index)
    if use_x:
        if xvar is None:
            raise ValueError(
                "brushedPoints: not able to automatically infer `xvar` from brush"
            )
        if xvar not in new_df:
            raise ValueError(f"brushedPoints: `xvar` ({xvar}) not in dataframe")
        keep_rows &= within_brush(new_df[xvar], brush, "x")

    if use_y:
        if yvar is None:
            raise ValueError(
                "brushedPoints: not able to automatically infer `yvar` from brush"
            )
        if yvar not in new_df:
            raise ValueError(f"brushedPoints: `yvar` ({yvar}) not in dataframe")
        keep_rows &= within_brush(new_df[yvar], brush, "y")

    # TODO: Find which rows are matches for the panel vars (if present)

    if all_rows:
        new_df["selected_"] = False
        new_df.loc[keep_rows, "selected_"] = True
    else:
        new_df = new_df.loc[keep_rows]

    return new_df


def near_points(
    df: pd.DataFrame,
    coordinfo: Union[CoordInfo, None],
    xvar: Optional[str] = None,
    yvar: Optional[str] = None,
    *,
    threshold: float = 5,
    add_dist: bool = False,
    all_rows: bool = False,
) -> pd.DataFrame:
    import numpy as np

    new_df = df.copy()

    # For no current coordinfo
    if coordinfo is None:
        if add_dist:
            new_df["dist"] = np.NaN

        if all_rows:
            new_df["selected_"] = False
        else:
            new_df = new_df.loc[[]]

        return new_df

    # Try to extract vars from coordinfo object
    coordinfo_mapping = coordinfo["mapping"]
    if xvar is None and "x" in coordinfo_mapping:
        xvar = coordinfo_mapping["x"]
    if yvar is None and "y" in coordinfo_mapping:
        yvar = coordinfo_mapping["y"]

    if xvar is None:
        raise ValueError(
            "nearPoints: not able to automatically infer `xvar` from coordinfo"
        )
    if yvar is None:
        raise ValueError(
            "nearPoints: not able to automatically infer `yvar` from coordinfo"
        )

    if xvar not in new_df.columns:
        raise ValueError(f"nearPoints: `xvar` ('{xvar}')  not in names of input")
    if yvar not in new_df.columns:
        raise ValueError(f"nearPoints: `yvar` ('{yvar}')  not in names of input")

    # TODO:
    # fortify discrete limits
    # as_number

    x: pd.Series[float] = df[xvar]
    y: pd.Series[float] = df[yvar]

    # Get the coordinates of the point (in img pixel coordinates)
    point_img: CoordXY = coordinfo["coords_img"]

    # Get coordinates of data points (in img pixel coordinates)
    data_img: SeriesXY = scale_coords(x, y, coordinfo)

    # Get x/y distances (in css coordinates)
    dist_css: SeriesXY = {
        "x": (data_img["x"] - point_img["x"]) / coordinfo["img_css_ratio"]["x"],
        "y": (data_img["y"] - point_img["y"]) / coordinfo["img_css_ratio"]["y"],
    }

    # Distances of data points to the target point, in css pixels.
    dists: pd.Series[float] = (dist_css["x"] ** 2 + dist_css["y"] ** 2) ** 0.5

    if add_dist:
        new_df["dist"] = dists

    keep_rows = dists <= threshold

    # # Find which rows are matches for the panel vars (if present)
    # if (!is.null(panelvar1))
    #     keep_rows <- keep_rows & panelMatch(coordinfo$panelvar1, df[[panelvar1]])
    # if (!is.null(panelvar2))
    #     keep_rows <- keep_rows & panelMatch(coordinfo$panelvar2, df[[panelvar2]])

    # Track the row indices to keep (note this is the row position, 0, 1, 2, not the
    # pandas index column, which can have arbitrary values).
    keep_idx = np.where(keep_rows)[0]  # pyright: reportUnknownMemberType=false

    # Order by distance
    dists = dists.iloc[keep_idx]
    keep_idx: npt.NDArray[np.intp] = keep_idx[dists.argsort()]

    # # Keep max number of rows
    # if (!is.null(maxpoints) && length(keep_idx) > maxpoints) {
    #     keep_idx <- keep_idx[seq_len(maxpoints)]
    # }

    if all_rows:
        # Add selected_ column if needed
        new_df["selected_"] = False
        new_df.iloc[
            keep_idx, new_df.columns.get_loc("selected_")
        ] = True  # pyright: reportUnknownArgumentType=false
    else:
        new_df = new_df.iloc[keep_idx]

    return new_df


# ===============================================================================
# Helper functions
# ===============================================================================
# Helper to determine if data values are within the limits of
# an input brush


def within_brush(
    vals: pd.Series[float], brush: BrushInfo, var: Literal["x", "y"] = "x"
) -> pd.Series[bool]:
    # brush = fortify_discrete_limits(brush)
    # vals = as_number(vals, brush["domain"]["discrete_limits"][var])
    # TODO: handle NAs?
    return (vals >= brush[var + "min"]) & (vals <= brush[var + "max"])


# ===============================================================================
# Scaling functions
# ===============================================================================
# These functions have direct analogs in Javascript code, except these are
# vectorized for x and y.

# Map a value x from a domain to a range. If clip is true, clip it to the
# range.
def map_linear(
    x: pd.Series[float],
    domain_min: float,
    domain_max: float,
    range_min: float,
    range_max: float,
    clip: bool = True,
) -> pd.Series[float]:
    factor = (range_max - range_min) / (domain_max - domain_min)
    val: pd.Series[float] = x - domain_min
    newval: pd.Series[float] = (val * factor) + range_min

    if clip:
        maxval = max(range_max, range_min)
        minval = min(range_max, range_min)
        newval[newval > maxval] = maxval
        newval[newval < minval] = minval

    return newval


# Scale val from domain to range. If logbase is present, use log scaling.
def scale_1d(
    val: pd.Series[float],
    domain_min: float,
    domain_max: float,
    range_min: float,
    range_max: float,
    logbase: Optional[float] = None,
    clip: bool = True,
) -> pd.Series[float]:
    import numpy as np

    if logbase is not None:
        val = np.log(val) / np.log(logbase)

    return map_linear(val, domain_min, domain_max, range_min, range_max, clip)


# Scale x and y coordinates from domain to range, using information in scaleinfo.
# scaleinfo must contain items $domain, $range, and $log. The scaleinfo object
# corresponds to one element from the coordmap object generated by getPrevPlotCoordmap
# or getGgplotCoordmap; it is the scaling information for one panel in a plot.
def scale_coords(
    x: pd.Series[float],
    y: pd.Series[float],
    coordinfo: CoordInfo,
) -> SeriesXY:
    domain = coordinfo["domain"]
    range = coordinfo["range"]
    log = coordinfo["log"]

    return {
        "x": scale_1d(
            x, domain["left"], domain["right"], range["left"], range["right"], log["x"]
        ),
        "y": scale_1d(
            y, domain["bottom"], domain["top"], range["bottom"], range["top"], log["y"]
        ),
    }
