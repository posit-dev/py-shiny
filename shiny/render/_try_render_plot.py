import base64
import io
import os
import sys
from typing import Optional, Union, cast, Tuple, TextIO, BinaryIO, Any, List

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol

from ..types import ImgData

# Use this protocol to avoid needing to maintain working stubs for matplotlib. If
# good stubs ever become available for matplotlib, use those instead.
class MplFigure(Protocol):
    def set_size_inches(
        self,
        w: Union[Tuple[float, float], float],
        h: Optional[float] = None,
        forward: bool = True,
    ):
        ...

    def savefig(
        self,
        fname: Union[str, TextIO, BinaryIO, "os.PathLike[Any]"],
        dpi: Union[float, Literal["figure"], None] = None,
        # facecolor="w",
        # edgecolor="w",
        # orientation="portrait",
        # papertype=None,
        format: Optional[str] = None,
        # transparent=False,
        bbox_inches: object = None,
        # pad_inches=0.1,
        # frameon=None,
        # metadata=None,
    ):
        ...


class MplArtist(Protocol):
    def get_figure(self) -> MplFigure:
        ...


class MplAnimation(Protocol):
    def pause(self):
        ...

    def resume(self):
        ...


# Use this protocol to avoid needing to maintain working stubs for plotnint. If
# good stubs ever become available for plotnine, use those instead.
class PlotnineFigure(Protocol):
    def save(
        self,
        filename: BinaryIO,
        format: str,
        units: str,
        dpi: float,
        width: float,
        height: float,
        verbose: bool,
        bbox_inches: object = None,
    ):
        ...


TryPlotResult = Tuple[bool, Union[ImgData, None]]


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
        fig.set_size_inches(width / ppi, height / ppi)

        bbox_inches = kwargs.pop("bbox_inches", "tight")

        with io.BytesIO() as buf:
            fig.savefig(
                buf,
                format="png",
                dpi=ppi * pixelratio,
                bbox_inches=bbox_inches,
                **kwargs,
            )
            buf.seek(0)
            data = base64.b64encode(buf.read())
            data_str = data.decode("utf-8")

        # N.B. matplotlib.tight_layout() causes the intrinsic file size can be different
        # from the requested size (i.e., the container size). So, scale the image to fit
        # in the container while preserving the aspect ratio.
        res: ImgData = {
            "src": "data:image/png;base64," + data_str,
            "width": "100%",
            "height": "100%",
            "style": "object-fit:contain",
        }

        if alt is not None:
            res["alt"] = alt

        return (True, res)

    finally:
        import matplotlib.pyplot  # pyright: ignore[reportMissingTypeStubs]

        matplotlib.pyplot.close(fig)  # pyright: ignore[reportUnknownMemberType]


def get_matplotlib_figure(x: object, allow_global: bool) -> Union[MplFigure, None]:
    from matplotlib.figure import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false
        Figure,
    )
    from matplotlib.artist import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false
        Artist,
    )
    from matplotlib.animation import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false
        Animation,
    )
    import matplotlib.pyplot as plt

    # Detect usage of pyplot global figure
    # TODO: Might be good to detect non-empty plt.get_fignums() before we call the user
    #   function, which would mean we will false-positive here. Maybe we warn in that
    #   case, maybe we ignore gcf(), maybe both.
    if (
        x is None and len(plt.get_fignums()) > 0
    ):  # pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
        if allow_global:
            return cast(MplFigure, plt.gcf())
        else:
            # Must close the global figure so we don't stay in this state forever
            plt.close(plt.gcf())
            raise RuntimeError(
                "matplotlib.pyplot cannot be used from an async render function; "
                "please use matplotlib's object-oriented interface instead"
            )

    if isinstance(x, Figure):
        return cast(MplFigure, x)

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
        return cast(MplArtist, x).get_figure()

    # Some other custom figure-like classes such as seaborn.axisgrid.FacetGrid attach
    # their figure as an attribute
    fig = getattr(x, "figure", None)
    if isinstance(fig, Figure):
        return cast(MplFigure, fig)

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
    import PIL.Image  # pyright: ignore[reportMissingModuleSource]

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
    from plotnine.ggplot import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false,reportMissingImports=false
        ggplot,
    )

    if not isinstance(x, ggplot):
        return (False, None)

    bbox_inches = kwargs.pop("bbox_inches", "tight")

    with io.BytesIO() as buf:
        cast(PlotnineFigure, x).save(
            filename=buf,
            format="png",
            units="in",
            dpi=ppi * pixelratio,
            width=width / ppi,
            height=height / ppi,
            verbose=False,
            bbox_inches=bbox_inches,
            **kwargs,
        )
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
