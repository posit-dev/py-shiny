from __future__ import annotations

from typing import Any, Dict, List, Optional, cast, overload

from htmltools import (
    HTMLDependency,
    Tag,
    TagChild,
    TagList,
    TagNode,
    head_content,
    tags,
)

from .._typing_extensions import TypeGuard
from ..session import Session, require_active_session
from ..types import MISSING, MISSING_TYPE


def shiny_input_label(id: str, label: TagChild = None) -> Tag:
    cls = "control-label" + ("" if label else " shiny-label-null")
    return tags.label(label, class_=cls, id=id + "-label", for_=id)


@overload
def get_window_title(
    title: None,
    window_title: MISSING_TYPE,
) -> None: ...


@overload
def get_window_title(
    title: None,
    window_title: str,
) -> HTMLDependency: ...


@overload
def get_window_title(
    title: str | Tag | TagList,
    window_title: str | MISSING_TYPE,
) -> HTMLDependency: ...


def get_window_title(
    title: Optional[str | Tag | TagList],
    window_title: str | MISSING_TYPE = MISSING,
) -> Optional[HTMLDependency]:
    if title is not None and isinstance(window_title, MISSING_TYPE):
        window_title = _find_child_strings(title)

    if isinstance(window_title, MISSING_TYPE):
        return None
    else:
        return head_content(tags.title(window_title))


def _find_child_strings(x: TagList | TagNode) -> str:
    if isinstance(x, Tag) and x.name not in ("script", "style"):
        x = x.children
    if isinstance(x, TagList):
        strings = [_find_child_strings(y) for y in x]
        return " ".join(filter(lambda x: x != "", strings))
    if isinstance(x, str):
        return x
    return ""


def _session_on_flush_send_msg(
    id: str, session: Session | None, msg: dict[str, object]
) -> None:
    session = require_active_session(session)
    session.on_flush(lambda: session.send_input_message(id, msg), once=True)


def is_01_scalar(x: object) -> TypeGuard[float]:
    return isinstance(x, (int, float)) and x >= 0.0 and x <= 1.0


def css_no_sub(**kwargs: str | float | None) -> Optional[str]:
    """
    Altered from py-htmltools's `css()`. Does not support substitutions of any kind.
    """
    res = ""
    for k, v in kwargs.items():
        if v is None:
            continue
        v = " ".join(v) if isinstance(v, list) else str(v)
        res += k + ":" + v + ";"
    return None if res == "" else res


class JSEval(str):
    pass


def js_eval(x: str) -> JSEval:
    """
    Mark a function as a JavaScript evaluation.
    Some components like `input_selectize` allow you to send JavaScript functions
    to the client.
    This function marks a string as a JavaScript evaluation so that it can be properly
    sent to the client library.
    """
    return JSEval(x)


def extract_js_keys(options: Dict[str, Any], parent_key: str = "") -> List[str]:
    """
    This function extracts JavaScript (JS) and HTML objects from the provided dictionary.
    This is used to identify which options should be evaluated by the client.

    Parameters:
    options (Dict[str, Any]): A dictionary containing various options and pulls out the keys
    of those options which are of type JSEval.

    Returns:
    A list of keys which identify the JSEval options
    """

    # TODO This only works on nested dictionaries, and we may need to extend it to
    # recurse through lists as well.
    js_html_keys: List[str] = []
    for key, value in options.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, JSEval):
            js_html_keys.append(full_key)
        elif isinstance(value, dict):
            value = cast(Dict[str, Any], value)
            js_html_keys.extend(extract_js_keys(value, full_key))
    return js_html_keys
