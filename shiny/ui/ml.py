from __future__ import annotations

from typing import Optional

__all__ = ("classification_label",)

import json

from htmltools import HTML, HTMLDependency, Tag, html_escape

from .. import __version__

# from .._docstring import add_example


def classification_label(
    value: dict[str, float],
    *,
    sort: bool = True,
    display_winner: Optional[bool] = None,
    max_items: Optional[int] = None,
    suffix: str = "%",
) -> Tag:
    """
    Create a classification label with confidence scores.

    This is meant to be used to display classification results from a model. The
    component itself is static, so to display dynamic values, it would typically be used
    with a :func:`~shiny.ui.ouput_ui` and :func:`~shiny.render.ui`.

    Parameters
    ----------
    value
        A dictionary with class names as keys and and confidence scores as values.
    sort
        Should the values be sorted? Defaults to ``True``.
    display_winner:
        If ``True`` (the default), then the name of the winner will be displayed above
        the values, in larger text.
    max_items:
        The maximum number of items to display. Defaults to ``None``, which means all
        items will be displayed.
    suffix:
        A string to place after each value. Defaults to ``"%"``.
    _add_ws:

    Returns
    -------
    :
        A UI element.
    """
    return Tag(
        "shiny-classification-label",
        ml_dep(),
        value=attr_to_escaped_json(value),
        sort=bool_to_num(sort),
        display_winner=bool_to_num(display_winner),
        max_items=max_items,
        suffix=suffix,
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
