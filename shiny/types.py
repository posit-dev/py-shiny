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

# Needed for NotRequired. See
#   https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
if sys.version_info < (3, 10):
    from __future__ import annotations

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

from typing import Union, Optional

# Sentinel value - indicates a missing value in a function call.
class MISSING_TYPE:
    pass


MISSING = MISSING_TYPE()


# Information about a single file, with a structure like:
#   {'name': 'mtcars.csv', 'size': 1303, 'type': 'text/csv', 'datapath: '/...../mtcars.csv'}
# The incoming data doesn't include 'datapath'; that field is added by the
# FileUploadOperation class.
class FileInfo(TypedDict):
    name: str
    size: int
    type: str
    datapath: str


class ImgData(TypedDict):
    src: str
    width: NotRequired[Union[str, float]]
    height: NotRequired[Union[str, float]]
    alt: NotRequired[Optional[str]]


class SafeException(Exception):
    pass


class SilentException(Exception):
    pass


class SilentCancelOutputException(Exception):
    pass
