from typing import Dict, cast

from ...session._utils import RenderedDeps
from ...types import ImgData
from ._renderer import JSONifiable

JSONifiable_dict = Dict[str, JSONifiable]


def rendered_deps_to_jsonifiable(rendered_deps: RenderedDeps) -> JSONifiable_dict:
    return cast(JSONifiable_dict, dict(rendered_deps))


def imgdata_to_jsonifiable(imgdata: ImgData) -> JSONifiable_dict:
    return cast(JSONifiable_dict, dict(imgdata))
