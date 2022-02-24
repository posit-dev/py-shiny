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

import sys
from typing import Union, Optional

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

from ._docstring import add_example

# Sentinel value - indicates a missing value in a function call.
class MISSING_TYPE:
    pass


MISSING = MISSING_TYPE()


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
    Return type for :func:`~shiny.render_image`.

    See Also
    --------
    ~shiny.render_image

    Example
    -------
    See :func:`~shiny.render_image`.
    """

    src: str
    """The ``src`` attribute of the ``<img>`` tag."""
    width: NotRequired[Union[str, float]]
    """The ``width`` attribute of the ``<img>`` tag."""
    height: NotRequired[Union[str, float]]
    """The ``height`` attribute of the ``<img>`` tag."""
    alt: NotRequired[Optional[str]]
    """The ``alt`` attribute of the ``<img>`` tag."""


@add_example()
class SafeException(Exception):
    """
    Throw a safe exception.

    When ``shiny.App.SANITIZE_ERRORS`` is ``True`` (which is the case
    in some production environments like RStudio Connect), exceptions are sanitized
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
        - This happens when the exception is raised from an output context (e.g., :func:`shiny.render_ui`)
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
