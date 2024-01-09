from __future__ import annotations

from typing import Any, Dict, cast

from htmltools import TagFunction

from ...session._utils import RenderedDeps
from ...types import MISSING_TYPE, ImgData
from ._renderer import Jsonifiable

JsonifiableDict = Dict[str, Jsonifiable]


def rendered_deps_to_jsonifiable(rendered_deps: RenderedDeps) -> JsonifiableDict:
    return cast(JsonifiableDict, dict(rendered_deps))


def imgdata_to_jsonifiable(imgdata: ImgData) -> JsonifiableDict:
    return cast(JsonifiableDict, dict(imgdata))


def set_kwargs_value(
    kwargs: dict[str, Any],
    key: str,
    ui_val: TagFunction | str | float | int | MISSING_TYPE,
    self_val: TagFunction | str | float | int | None | MISSING_TYPE,
):
    """
    Set kwarg value with fallback value.

    * If `ui_val` is not `MISSING`, set `kwargs[key] = ui_val`.
    * If `self_val` is not `MISSING` and is not `None`, set `kwargs[key] = self_val`.
    * Otherwise, do nothing.
    """
    if not isinstance(ui_val, MISSING_TYPE):
        kwargs[key] = ui_val
        return
    if not (isinstance(self_val, MISSING_TYPE) or self_val is None):
        kwargs[key] = self_val
        return
    # Do nothing as we don't want to override the default value (that could change in the future)
    return
