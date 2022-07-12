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


TryPlotResult = Union[ImgData, None, Literal["TYPE_MISMATCH"]]


# Try to render a matplotlib object. If `fig` is not a matplotlib object, return
# "TYPE_MISMATCH". If there's an error in rendering, return None. If successful in
# rendering, return an ImgData object.
def try_render_matplotlib(
    x: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
    **kwargs: object,
) -> TryPlotResult:
    fig = get_matplotlib_figure(x)

    if fig is None:
        return "TYPE_MISMATCH"

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

        return res

    except Exception as e:
        # TODO: just let errors propagate?
        print("Error rendering matplotlib object: " + str(e))

    finally:
        import matplotlib.pyplot  # pyright: ignore[reportMissingTypeStubs]

        matplotlib.pyplot.close(fig)  # pyright: ignore[reportUnknownMemberType]

    return None


def get_matplotlib_figure(x: object) -> Union[MplFigure, None]:
    from matplotlib.figure import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false
        Figure,
    )
    from matplotlib.artist import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false
        Artist,
    )
    from matplotlib.animation import (  # pyright: reportMissingTypeStubs=false,reportUnknownVariableType=false
        Animation,
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
        figs = [get_matplotlib_figure(y) for y in cast(List[Any], x)]
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
        return "TYPE_MISMATCH"

    try:
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

        return res

    except Exception as e:
        # TODO: just let errors propagate?
        print("Error rendering PIL object: " + str(e))

    return None


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
        return "TYPE_MISMATCH"

    bbox_inches = kwargs.pop("bbox_inches", "tight")
    try:
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

        return res

    except Exception as e:
        # TODO: just let errors propagate?
        print("Error rendering matplotlib object: " + str(e))

    return None
