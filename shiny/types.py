__all__ = ("MISSING", "MISSING_TYPE", "FileInfo", "ImgData")

import sys
from typing import Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from typing_extensions import NotRequired

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
    alt: NotRequired[str]
