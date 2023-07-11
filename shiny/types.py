# Needed for NotRequired with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

__all__ = (
    "MISSING",
    "MISSING_TYPE",
    "FileInfo",
    "ImgData",
    "SafeException",
    "SilentException",
    "SilentCancelOutputException",
)

from typing import TYPE_CHECKING, Any, BinaryIO, Literal, Optional, Protocol

from htmltools import TagChild

from ._docstring import add_example
from ._typing_extensions import NotRequired, TypedDict

if TYPE_CHECKING:
    from matplotlib.figure import Figure


# Sentinel value - indicates a missing value in a function call.
class MISSING_TYPE:
    pass


MISSING: MISSING_TYPE = MISSING_TYPE()


# Information about a single file, with a structure like:
#   {'name': 'mtcars.csv', 'size': 1303, 'type': 'text/csv', 'datapath: '/...../mtcars.csv'}
# The incoming data doesn't include 'datapath'; that field is added by the
# FileUploadOperation class.
class FileInfo(TypedDict):
    """
    Information about a file upload.

    See Also
    --------
    ~shiny.ui.input_file

    Example
    -------
    See :func:`~shiny.ui.input_file`.
    """

    name: str
    """The name of the file."""
    size: int
    """The size of the file in bytes."""
    type: str
    """The MIME type of the file."""
    datapath: str
    """The path to the file on the server."""


class ImgData(TypedDict):
    """
    Return type for :func:`~shiny.render.image`.

    See Also
    --------
    ~shiny.render.image

    Example
    -------
    See :func:`~shiny.render.image`.
    """

    src: str
    """The ``src`` attribute of the ``<img>`` tag."""
    width: NotRequired[str | float]
    """The ``width`` attribute of the ``<img>`` tag."""
    height: NotRequired[str | float]
    """The ``height`` attribute of the ``<img>`` tag."""
    alt: NotRequired[str]
    """The ``alt`` attribute of the ``<img>`` tag."""
    style: NotRequired[str]
    """The ``style`` attribute of the ``<img>`` tag."""
    coordmap: NotRequired[Any]
    """TODO """


@add_example()
class SafeException(Exception):
    """
    Throw a safe exception.

    When ``shiny.App.SANITIZE_ERRORS`` is ``True`` (which is the case
    in some production environments like Posit Connect), exceptions are sanitized
    to prevent leaking of sensitive information. This class provides a way to
    generate an error that is OK to be displayed to the user.
    """

    pass


@add_example()
class SilentException(Exception):
    """
    Throw a silent exception.

    Normally, when an exception occurs inside a reactive context, it's either:

    - Displayed to the user (as a big red error message)
        - This happens when the exception is raised from an output context (e.g., :func:`shiny.render.ui`)
    - Crashes the application
        - This happens when the exception is raised from an :func:`shiny.reactive.Effect`

    This exception is used to silently throw inside a reactive context, meaning that
    execution is paused, and no output is shown to users (or the python console).

    See Also
    --------
    ~SilentCancelOutputException
    """

    pass


@add_example()
class SilentCancelOutputException(Exception):
    """
    Throw a silent exception and don't clear output

    Similar to :class:`~SilentException`, but if thrown in an output context,
    existing output isn't cleared.

    See Also
    --------
    ~SilentException
    """

    pass


class ActionButtonValue(int):
    pass


class NavSetArg(Protocol):
    """
    An value suitable for passing to a navigation container (e.g.,
    :func:`~shiny.ui.navset_tab`).
    """

    def resolve(
        self, selected: Optional[str], context: dict[str, Any]
    ) -> tuple[TagChild, TagChild]:
        """
        Resolve information provided by the navigation container.

        Parameters
        ----------
        selected
            The value of the navigation item to be shown on page load.
        context
            Additional context supplied by the navigation container.
        """
        ...

    def get_value(self) -> Optional[str]:
        """
        Get the value of this navigation item (if any).

        This value is only used to determine what navigation item should be shown
        by default when none is specified (i.e., the first navigation item that
        returns a value is used to determine the container's ``selected`` value).
        """
        ...


# =============================================================================
# Types for plots and images
# =============================================================================


# Use this protocol to avoid needing to maintain working stubs for plotnint. If
# good stubs ever become available for plotnine, use those instead.
class PlotnineFigure(Protocol):
    scales: list[Any]
    coordinates: Any
    facet: Any
    layout: Any
    mapping: dict[str, str]

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

    def draw(self, show: bool) -> Figure:
        ...


class CoordmapDims(TypedDict):
    width: float
    height: float


class CoordmapPanelLog(TypedDict):
    x: float | None
    y: float | None


class CoordmapPanelDomain(TypedDict):
    left: float
    right: float
    bottom: float
    top: float


class CoordmapPanelRange(TypedDict):
    left: float
    right: float
    bottom: float
    top: float


class CoordmapPanelMapping(TypedDict):
    x: str | None
    y: str | None
    panelvar1: NotRequired[str]
    panelvar2: NotRequired[str]


class CoordmapPanelvarValues(TypedDict):
    panelvar1: NotRequired[float]
    panelvar2: NotRequired[float]


class CoordmapPanel(TypedDict):
    panel: int
    row: NotRequired[int]
    col: NotRequired[int]
    panel_vars: NotRequired[CoordmapPanelvarValues]
    log: CoordmapPanelLog
    domain: CoordmapPanelDomain
    mapping: CoordmapPanelMapping
    range: CoordmapPanelRange


class Coordmap(TypedDict):
    panels: list[CoordmapPanel]
    dims: CoordmapDims


class CoordXY(TypedDict):
    x: float
    y: float


# Data structure sent from client to server when a plot is clicked, double-clicked, or
# hovered.
class CoordInfo(TypedDict):
    x: float
    y: float
    coords_css: CoordXY
    coords_img: CoordXY
    img_css_ratio: CoordXY
    panelvar1: NotRequired[str]
    panelvar2: NotRequired[str]
    mapping: CoordmapPanelMapping
    domain: CoordmapPanelDomain
    range: CoordmapPanelRange
    log: CoordmapPanelLog
    # .nonce: float


class BrushInfo(TypedDict):
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    coords_css: CoordXY
    coords_img: CoordXY
    img_css_ratio: CoordXY
    panelvar1: NotRequired[str]
    panelvar2: NotRequired[str]
    mapping: CoordmapPanelMapping
    domain: CoordmapPanelDomain
    range: CoordmapPanelRange
    log: CoordmapPanelLog
    direction: Literal["x", "y", "xy"]
    # .nonce: float
