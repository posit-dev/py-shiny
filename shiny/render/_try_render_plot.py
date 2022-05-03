import base64
import io
import os
import sys
from typing import Optional, Union, cast, Tuple, TextIO, BinaryIO, Any

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol
else:
    from typing_extensions import Literal, Protocol

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


TryPlotResult = Union[ImgData, None, Literal["TYPE_MISMATCH"]]


# Try to render a matplotlib object. If `fig` is not a matplotlib object, return
# "TYPE_MISMATCH". If there's an error in rendering, return None. If successful in
# rendering, return an ImgData object.
def try_render_matplotlib(
    fig: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
) -> TryPlotResult:
    import matplotlib.figure  # pyright: ignore[reportMissingTypeStubs]
    import matplotlib.pyplot  # pyright: ignore[reportMissingTypeStubs]

    if isinstance(
        fig, matplotlib.figure.Figure  # pyright: ignore[reportUnknownMemberType]
    ):
        mpl = cast(MatplotlibFigureProtocol, fig)
        try:
            mpl.set_dpi(ppi * pixelratio)
            mpl.set_size_inches(width / ppi, height / ppi)

            with io.BytesIO() as buf:
                mpl.savefig(buf, format="png")
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
            matplotlib.pyplot.close(fig)  # pyright: ignore[reportUnknownMemberType]

        return None

    else:
        return "TYPE_MISMATCH"


def try_render_pil(
    fig: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
) -> TryPlotResult:
    import PIL.Image

    if isinstance(fig, PIL.Image.Image):
        try:
            with io.BytesIO() as buf:
                fig.save(buf, format="PNG")
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

    else:
        return "TYPE_MISMATCH"
