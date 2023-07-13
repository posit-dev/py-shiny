# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

import base64
import io
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, cast

from ..types import ImgData, PlotnineFigure
from ._coordmap import get_coordmap, get_coordmap_plotnine

TryPlotResult = Tuple[bool, "ImgData| None"]


if TYPE_CHECKING:
    from matplotlib.figure import Figure


# Try to render a matplotlib object (or the global figure, if it's been used). If `fig`
# is not a matplotlib object, return (False, None). If there's an error in rendering,
# return None. If successful in rendering, return an ImgData object.
def try_render_matplotlib(
    x: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    allow_global: bool,
    alt: Optional[str],
    **kwargs: object,
) -> TryPlotResult:
    fig = get_matplotlib_figure(x, allow_global)

    if fig is None:
        return (False, None)

    try:
        import matplotlib.pyplot as plt

        fig.set_size_inches(width / ppi, height / ppi)
        fig.set_dpi(ppi * pixelratio)

        plt.tight_layout()  # pyright: ignore[reportUnknownMemberType]
        coordmap = get_coordmap(fig)

        with io.BytesIO() as buf:
            fig.savefig(  # pyright: ignore[reportUnknownMemberType]
                buf,
                format="png",
                dpi=ppi * pixelratio,
                **kwargs,
            )
            buf.seek(0)
            data = base64.b64encode(buf.read())
            data_str = data.decode("utf-8")

        res: ImgData = {
            "src": "data:image/png;base64," + data_str,
            "width": "100%",
            "height": "100%",
        }

        if alt is not None:
            res["alt"] = alt

        if coordmap is not None:
            res["coordmap"] = coordmap

        return (True, res)

    finally:
        import matplotlib.pyplot

        matplotlib.pyplot.close(fig)  # pyright: ignore[reportUnknownMemberType]


def get_matplotlib_figure(
    x: object, allow_global: bool
) -> Figure | None:  # pyright: ignore
    import matplotlib.pyplot as plt
    from matplotlib.animation import Animation
    from matplotlib.artist import Artist
    from matplotlib.figure import Figure

    # Detect usage of pyplot global figure
    # TODO: Might be good to detect non-empty plt.get_fignums() before we call the user
    #   function, which would mean we will false-positive here. Maybe we warn in that
    #   case, maybe we ignore gcf(), maybe both.
    if x is None and len(plt.get_fignums()) > 0:
        if allow_global:
            return plt.gcf()
        else:
            # Must close the global figure so we don't stay in this state forever
            plt.close(plt.gcf())  # pyright: ignore[reportUnknownMemberType]
            raise RuntimeError(
                "matplotlib.pyplot cannot be used from an async render function; "
                "please use matplotlib's object-oriented interface instead"
            )

    if isinstance(x, Figure):
        return x

    if isinstance(x, Animation):
        raise RuntimeError(
            "Matplotlib's Animation class isn't supported by @render.plot. "
            + "Consider explictly saving the animation to a file and "
            + "then using @render.image instead to render it."
        )

    # Libraries like pandas, xarray, etc have plot() methods that can return a wide
    # array pf mpl classes, like Lines2D, Subplots, Axes, etc. The Artist ABC class
    # should cover most, if not all, of these (it doesn't cover Animation, though).
    # https://matplotlib.org/stable/api/artist_api.html
    if isinstance(x, Artist):
        return x.get_figure()

    # Some other custom figure-like classes such as seaborn.axisgrid.FacetGrid attach
    # their figure as an attribute
    fig = getattr(x, "figure", None)
    if isinstance(fig, Figure):
        return fig

    # Sometimes generic plot() methods will return an iterable of Artists,
    # If they all refer to the same figure, then it seems reasonable to use it
    # https://docs.xarray.dev/en/latest/user-guide/plotting.html#dimension-along-y-axis
    if isinstance(x, (list, tuple)):
        figs = [get_matplotlib_figure(y, allow_global) for y in cast(List[Any], x)]
        if len(set(figs)) == 1:
            return figs[0]

    return None


def try_render_pil(
    x: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
    **kwargs: object,
) -> TryPlotResult:
    import PIL.Image

    if not isinstance(x, PIL.Image.Image):
        return (False, None)

    with io.BytesIO() as buf:
        x.save(buf, format="PNG", **kwargs)
        buf.seek(0)
        data = base64.b64encode(buf.read())
        data_str = data.decode("utf-8")

    res: ImgData = {
        "src": "data:image/png;base64," + data_str,
        "width": "100%",
        "height": "100%",
        "style": "object-fit:contain",
    }

    if alt is not None:
        res["alt"] = alt

    return (True, res)


def try_render_plotnine(
    x: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
    **kwargs: object,
) -> TryPlotResult:
    from plotnine.ggplot import ggplot

    if not isinstance(x, ggplot):
        return (False, None)

    x = cast(PlotnineFigure, x)

    with io.BytesIO() as buf:
        # save_helper was added in plotnine 0.10.1-dev. If this method exists, we can
        # use it to get the matplotlib Figure object, which we can then use to get the
        # coordmap. Once this version of plotnine is released and in common use, we can
        # add a version dependency and remove the conditional code.
        if hasattr(x, "save_helper"):
            res = x.save_helper(  # pyright: ignore[reportUnknownMemberType, reportGeneralTypeIssues, reportUnknownVariableType]
                filename=buf,
                format="png",
                units="in",
                dpi=ppi * pixelratio,
                width=width / ppi,
                height=height / ppi,
                verbose=False,
                **kwargs,
            )
            coordmap = get_coordmap_plotnine(
                x,
                res.figure,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportGeneralTypeIssues]
            )
            res.figure.savefig(  # pyright: ignore[reportUnknownMemberType, reportGeneralTypeIssues]
                **res.kwargs  # pyright: ignore[reportUnknownMemberType, reportGeneralTypeIssues]
            )
        else:
            x.save(
                filename=buf,
                format="png",
                units="in",
                dpi=ppi * pixelratio,
                width=width / ppi,
                height=height / ppi,
                verbose=False,
                **kwargs,
            )
            coordmap = None
        buf.seek(0)
        data = base64.b64encode(buf.read())
        data_str = data.decode("utf-8")

    res: ImgData = {
        "src": "data:image/png;base64," + data_str,
        "width": "100%",
        "height": "100%",
    }

    if alt is not None:
        res["alt"] = alt

    if coordmap is not None:
        res["coordmap"] = coordmap

    return (True, res)
