import base64
import io
import os
import sys
from typing import (
    Optional,
    Union,
    cast,
    Tuple,
    TextIO,
    BinaryIO,
    Any,
    List,
    TYPE_CHECKING,
)

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol

if TYPE_CHECKING:
    from matplotlib.figure import Figure

from ..types import ImgData

# Use this protocol to avoid needing to maintain working stubs for matplotlib. If
# good stubs ever become available for matplotlib, use those instead.
class MatplotlibFigureProtocol(Protocol):
    def set_dpi(self, val: float) -> None:
        ...

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
        # dpi: Union[float, Literal["figure"], None] = None,
        # facecolor="w",
        # edgecolor="w",
        # orientation="portrait",
        # papertype=None,
        format: Optional[str] = None,
        # transparent=False,
        # bbox_inches=None,
        # pad_inches=0.1,
        # frameon=None,
        # metadata=None,
    ):
        ...


# Use this protocol to avoid needing to maintain working stubs for plotnint. If
# good stubs ever become available for plotnine, use those instead.
class PlotnineFigureProtocol(Protocol):
    def save(
        self,
        filename: BinaryIO,
        format: str,
        units: str,
        dpi: float,
        width: float,
        height: float,
        verbose: bool,
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
) -> TryPlotResult:
    fig = get_matplotlib_figure(x)

    if fig is None:
        return "TYPE_MISMATCH"

    try:
        figure = cast(MatplotlibFigureProtocol, fig)
        figure.set_dpi(ppi * pixelratio)
        figure.set_size_inches(width / ppi, height / ppi)

        with io.BytesIO() as buf:
            figure.savefig(buf, format="png")
            buf.seek(0)
            data = base64.b64encode(buf.read())
            data_str = data.decode("utf-8")

        res: ImgData = {
            "src": "data:image/png;base64," + data_str,
            "width": width,
            "height": height,
            "alt": alt,
        }

        return res

    except Exception as e:
        # TODO: just let errors propagate?
        print("Error rendering matplotlib object: " + str(e))

    finally:
        import matplotlib.pyplot  # pyright: ignore[reportMissingTypeStubs]

        matplotlib.pyplot.close(fig)  # pyright: ignore[reportUnknownMemberType]

    return None


def get_matplotlib_figure(x: object) -> Union["Figure", None]:
    from matplotlib.figure import Figure
    from matplotlib.artist import Artist
    from matplotlib.animation import Animation

    if isinstance(x, Figure):
        return x

    if isinstance(x, Animation):
        raise RuntimeError(
            "Matplotlib's Animation class isn't supported by @render_plot(). "
            + "Consider explictly saving the animation to a file and "
            + "then using @render_image() instead to render it."
        )

    # Libraries like pandas, xarray, etc have plot() methods that can return a wide
    # array pf mpl classes, like Lines2D, Subplots, Axes, etc. The Artist ABC class
    # should cover most, if not all, of these (it doesn't cover Animation, though).
    # https://matplotlib.org/stable/api/artist_api.html
    if isinstance(x, Artist):
        return x.get_figure()

    # Sometimes generic plot() methods will return an iterable of Artists,
    # If they all refer to the same figure, then it seems reasonable to use it
    # https://docs.xarray.dev/en/latest/user-guide/plotting.html#dimension-along-y-axis
    if isinstance(x, (list, tuple)):
        figs = [get_matplotlib_figure(y) for y in cast(List[Any], x)]
        if len(set(figs)) == 1:
            return figs[0]

    # holoviews has it's own figure representations, most (all?) of which may be
    # "rendered" to bokeh or mpl Figure/Animation objects.
    # TODO: does this work for holoviews extension packages?
    if "holoviews" in sys.modules and x.__module__.split(".")[0] == "holoviews":
        import holoviews

        return get_matplotlib_figure(holoviews.render(x, backend="matplotlib"))  # type: ignore

    return None


def try_render_pil(
    x: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
) -> TryPlotResult:
    import PIL.Image

    if not isinstance(x, PIL.Image.Image):
        return "TYPE_MISMATCH"

    try:
        with io.BytesIO() as buf:
            x.save(buf, format="PNG")
            buf.seek(0)
            data = base64.b64encode(buf.read())
            data_str = data.decode("utf-8")

        res: ImgData = {
            "src": "data:image/png;base64," + data_str,
            "width": width,
            "height": height,
            "alt": alt,
        }

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
) -> TryPlotResult:
    from plotnine.ggplot import ggplot

    if not isinstance(x, ggplot):
        return "TYPE_MISMATCH"

    try:
        with io.BytesIO() as buf:
            cast(PlotnineFigureProtocol, x).save(
                filename=buf,
                format="png",
                units="in",
                dpi=ppi * pixelratio,
                width=width / ppi,
                height=height / ppi,
                verbose=False,
            )
            buf.seek(0)
            data = base64.b64encode(buf.read())
            data_str = data.decode("utf-8")

        res: ImgData = {
            "src": "data:image/png;base64," + data_str,
            "width": width,
            "height": height,
            "alt": alt,
        }

        return res

    except Exception as e:
        # TODO: just let errors propagate?
        print("Error rendering matplotlib object: " + str(e))

    return None
