from __future__ import annotations

from typing import Optional

__all__ = ("classification_label",)

import json

from htmltools import HTML, HTMLDependency, Tag, TagAttrValue, html_escape

from .. import __version__

# from .._docstring import add_example
# from .._namespaces import resolve_id


def classification_label(
    value: dict[str, float],
    *,
    sort: Optional[bool] = None,
    display_winner: Optional[bool] = None,
    _add_ws: bool = True,
    **kwargs: TagAttrValue,
) -> Tag:
    return Tag(
        "shiny-classification-label",
        ml_dep(),
        value=attr_to_escaped_json(value),
        sort=bool_to_num(sort),
        display_winner=bool_to_num(display_winner),
        _add_ws=_add_ws,
        **kwargs,
    )


def attr_to_escaped_json(x: object) -> str:
    res = json.dumps(x)
    res = html_escape(res, attr=True)
    return HTML(res)


def bool_to_num(x: bool | None) -> int | None:
    if x is None:
        return None
    if x:
        return 1
    else:
        return 0


def ml_dep() -> HTMLDependency:
    return HTMLDependency(
        name="shiny-ml-components",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "www/shared/ml",
        },
        script={"src": "ml.js", "type": "module"},
    )
