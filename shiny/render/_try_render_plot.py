from __future__ import annotations

import base64
import io
import warnings
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Tuple, Union, cast

from ..types import ImgData, PlotnineFigure
from ._coordmap import get_coordmap, get_coordmap_plotnine

TryPlotResult = Tuple[bool, Union[ImgData, None]]


if TYPE_CHECKING:
    from matplotlib.figure import Figure


class PlotSizeInfo:
    """This class carries information from the render.plot transformer to the logic that
    actually renders the plot to PNG. It also encapsulates the tricky logic for figuring
    out what the image size and attributes should be."""

    def __init__(
        self,
        container_size_px_fn: tuple[Callable[[], float], Callable[[], float]],
        user_specified_size_px: tuple[float | None, float | None],
        pixelratio: float,
    ):
        """
        Parameters
        ----------
        container_size_px_fn
            A tuple of two functions that return the width and height of the container,
            in pixels. If the user specified an explicit width/height on the
            @render.plot decorator, then these functions should not be called, as doing
            so will take a reactive dependency on that dimension.
        user_specified_size_px
            A tuple of two floats, or None. If the user specified an explicit
            width/height on the @render.plot decorator, then the corresponding float
            will be that value. Otherwise, it will be None.
        pixelratio
            The device pixel ratio that was detected from the client.
        """
        self._container_size_px_fn = container_size_px_fn
        self.user_specified_size_px = user_specified_size_px
        self.pixelratio = pixelratio

    def get_img_size_px(
        self,
        fig_initial_size_inches: tuple[float, float],
        fig_result_size_inches: tuple[float, float],
        dpi: float,
    ) -> tuple[float, float, str, str]:
        """
        Determines the desired size of the image in logical pixels (not doubling
        resolution for retina displays--the caller needs to worry about that), and the
        width and height attributes that should be set on the <img> tag.

        Parameters
        ----------
        fig_initial_size_inches
            The default matplotlib/plotnine figure size.
        fig_result_size_inches
            The size of the matplotlib/plotnine figure that the user created. If this is
            different than fig_initial_size_inches, we'll respect it. Otherwise, we'll
            use the container size instead.
        dpi
            The desired DPI of the image.

        Returns
        -------
        :
            A tuple of (width, height, width_attr, height_attr), where width and height
            are the desired size of the image in CSS pixels, and width_attr and
            height_attr are the width and height attributes that should be set on the
            <img> tag. The width and height attributes may differ from the width and
            height values because when we use the container size as the image size, we
            set the width/height attributes to 100% so that the image will continuously
            fill the container even as the container is resized (i.e. the re-render
            hasn't happened yet).
        """
        w, w_attr = self._get_img_size_px(
            0,
            fig_initial_size_inches[0],
            fig_result_size_inches[0],
            dpi,
        )
        h, h_attr = self._get_img_size_px(
            1,
            fig_initial_size_inches[1],
            fig_result_size_inches[1],
            dpi,
        )
        return (w, h, w_attr, h_attr)

    def _get_img_size_px(
        self,
        i: int,
        fig_initial_size_inches: float,
        fig_result_size_inches: float,
        dpi: float,
    ) -> tuple[float, str]:
        # If user specified explicit width/height on @render.plot decorator, set the img
        # size to that exactly. We assume there's some reason they wanted that exact size.
        user_specified_size_px = self.user_specified_size_px[i]
        if user_specified_size_px is not None:
            if user_specified_size_px == 0:
                # If the explicit size is 0, we'll respect the user's figure size.
                native_size = fig_result_size_inches * dpi
                return native_size, f"{native_size}px"
            else:
                return user_specified_size_px, f"{user_specified_size_px}px"

        # If the user didn't specify an explicit size on @render.plot then assume that
        # they're filling the container, in which case we set the img size to 100% in
        # order to have nicer resize behavior.
        #
        # Retrieve the container size, taking a reactive dependency
        container_size_px = self._container_size_px_fn[i]()
        return container_size_px, "100%"


# Try to render a matplotlib object (or the global figure, if it's been used). If `fig`
# is not a matplotlib object, return (False, None). If there's an error in rendering,
# return None. If successful in rendering, return an ImgData object.
def try_render_matplotlib(
    x: object,
    *,
    plot_size_info: PlotSizeInfo,
    allow_global: bool,
    alt: Optional[str],
    **kwargs: object,
) -> TryPlotResult:
    fig = get_matplotlib_figure(x, allow_global)

    if fig is None:
        return (False, None)

    try:
        import matplotlib
        import matplotlib.pyplot as plt  # pyright: ignore[reportUnusedImport] # noqa: F401

        pixelratio = plot_size_info.pixelratio

        fig_initial_size_inches = cast_to_size_tuple(plt.rcParams["figure.figsize"])

        fig_result_size_inches = cast_to_size_tuple(
            fig.get_size_inches(),  # pyright: ignore[reportUnknownMemberType]
        )

        ppi_out = get_desired_dpi_from_fig(fig)

        width, height, width_attr, height_attr = plot_size_info.get_img_size_px(
            fig_initial_size_inches, fig_result_size_inches, ppi_out
        )
        fig.set_size_inches(
            width / ppi_out,
            height / ppi_out,
        )
        fig.set_dpi(ppi_out * pixelratio)

        # Calculating accurate coordinate mappings requires that the layout engine
        # (if there is one) adjusts the figure's subplot parameters.
        # e.g. "tight" layout.
        # When there is no layout engine, "tight" layout is often helpful
        layout_engine = None
        # get_layout_engine was added in matplotlib 3.6
        if hasattr(fig, "get_layout_engine"):
            layout_engine = fig.get_layout_engine()
            if layout_engine:
                if not layout_engine.adjust_compatible:
                    # In most cases, this branch will override the constained layout.
                    # which is usually a very deliberate choice by the user
                    fig.set_layout_engine(  # pyright: ignore[reportUnknownMemberType]
                        layout="tight"
                    )
                    warnings.warn(
                        f"'{type(layout_engine)}' layout engine is not compatible with shiny. "
                        "The figure layout has been changed to tight.",
                        stacklevel=1,
                    )
            else:
                fig.set_layout_engine(  # pyright: ignore[reportUnknownMemberType]
                    layout="tight"
                )
        else:
            # This branch needed for matplotlib <3.6. Eventually we will be able to
            # remove this code path.

            # Suppress the message `UserWarning: The figure layout has changed to tight`
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    action="ignore",
                    category=UserWarning,
                    message="The figure layout has changed to tight",
                )
            plt.tight_layout()  # pyright: ignore[reportUnknownMemberType]

        with io.BytesIO() as buf:
            fig.savefig(  # pyright: ignore[reportUnknownMemberType]
                buf,
                format="png",
                dpi=ppi_out * pixelratio,
                **kwargs,  # pyright: ignore[reportArgumentType, reportGeneralTypeIssues]
            )
            buf.seek(0)
            data = base64.b64encode(buf.read())
            data_str = data.decode("utf-8")

        # Calculating accurate coordinate mappings requires the figure to be
        # drawn/saved first, which runs the layout engine.
        coordmap = get_coordmap(fig)

        res: ImgData = {
            "src": "data:image/png;base64," + data_str,
            "width": width_attr,
            "height": height_attr,
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
    *,
    plot_size_info: PlotSizeInfo,
    alt: Optional[str] = None,
    **kwargs: object,
) -> TryPlotResult:
    import PIL.Image

    if not isinstance(x, PIL.Image.Image):
        return (False, None)

    with io.BytesIO() as buf:
        x.save(  # pyright: ignore[reportUnknownMemberType]
            buf,
            format="PNG",
            **kwargs,  # pyright: ignore[reportArgumentType,reportGeneralTypeIssues]
        )
        buf.seek(0)
        data = base64.b64encode(buf.read())
        data_str = data.decode("utf-8")

    width_attr = plot_size_info.user_specified_size_px[0]
    width_attr = f"{width_attr}px" if width_attr is not None else "100%"
    height_attr = plot_size_info.user_specified_size_px[1]
    height_attr = f"{height_attr}px" if height_attr is not None else "100%"

    res: ImgData = {
        "src": "data:image/png;base64," + data_str,
        "width": width_attr,
        "height": height_attr,
        "style": "object-fit:contain",
    }

    if alt is not None:
        res["alt"] = alt

    return (True, res)


def try_render_plotnine(
    x: object,
    *,
    plot_size_info: PlotSizeInfo,
    alt: Optional[str] = None,
    **kwargs: object,
) -> TryPlotResult:
    import plotnine.options as p9options
    from plotnine.ggplot import ggplot

    if not isinstance(x, ggplot):
        return (False, None)

    fig_initial_size_inches = p9options.figure_size

    x = cast(PlotnineFigure, x)

    fig_result_size_inches = fig_initial_size_inches
    figure_size = x.theme.themeables.get("figure_size")
    if figure_size is not None:
        result_size = figure_size.properties.get("value")
        if result_size is not None:
            fig_result_size_inches = result_size
    ppi = p9options.dpi
    figure_dpi = x.theme.themeables.get("dpi")
    if figure_dpi is not None:
        result_dpi = figure_dpi.properties.get("value")
        if result_dpi is not None:
            ppi = result_dpi

    w, h, w_attr, h_attr = plot_size_info.get_img_size_px(
        fig_initial_size_inches, fig_result_size_inches, ppi
    )

    with io.BytesIO() as buf:
        if not hasattr(x, "save_helper"):
            raise RuntimeError(
                "plotnine>=0.10.1 is required to render plotnine plots in Shiny"
            )
        res = x.save_helper(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownVariableType, reportGeneralTypeIssues]
            filename=buf,
            format="png",
            units="in",
            dpi=ppi * plot_size_info.pixelratio,
            width=w / ppi,
            height=h / ppi,
            verbose=False,
            **kwargs,
        )
        res.figure.savefig(  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportGeneralTypeIssues]
            **res.kwargs  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue, reportGeneralTypeIssues]
        )
        buf.seek(0)
        data = base64.b64encode(buf.read())
        data_str = data.decode("utf-8")

    # Calculating accurate coordinate mappings requires the figure to be
    # drawn/saved first, which runs the layout engine.
    coordmap = get_coordmap_plotnine(
        x,
        res.figure,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue, reportGeneralTypeIssues]
    )

    res: ImgData = {
        "src": "data:image/png;base64," + data_str,
        "width": w_attr,
        "height": h_attr,
    }

    if alt is not None:
        res["alt"] = alt

    if coordmap is not None:
        res["coordmap"] = coordmap

    return (True, res)


# This is a weird one... the default dpi is not set to rcParam["figure.dpi"], but rather
# to rcParam["figure.dpi"] * fig.canvas.device_pixel_ratio (which is 2.0 on my Mac with
# the 'MacOSX' mpl backend). We want to undo that scaling, as it makes the text
# ridiculously large.
#
# One negative consequence of this logic: if the user intentionally set the dpi to
# rcParam * device_pixel_ratio, we're going to ignore it.
def get_desired_dpi_from_fig(fig: Figure) -> float:
    ppi_out = fig.get_dpi()

    if fig.canvas.device_pixel_ratio != 1 and hasattr(fig, "_original_dpi"):
        if fig._original_dpi == ppi_out / fig.canvas.device_pixel_ratio:  # type: ignore
            return cast(float, fig._original_dpi)  # type: ignore
    return ppi_out


def cast_to_size_tuple(lst: Any) -> tuple[float, float]:
    return cast(Tuple[float, float], tuple(lst))
