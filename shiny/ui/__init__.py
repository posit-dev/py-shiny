"""
Tools for creating user interfaces including: custom components, HTML components,
layout helpers, page-level containers, and more.
"""

# All objects imported into this scope will be available as shiny.ui.foo
from ._bootstrap import *  # noqa: F401
from ._download_button import *  # noqa: F401
from ._input_action_button import *  # noqa: F401
from ._input_check_radio import *  # noqa: F401
from ._input_date import *  # noqa: F401
from ._input_file import *  # noqa: F401
from ._input_numeric import *  # noqa: F401
from ._input_password import *  # noqa: F401
from ._input_select import *  # noqa: F401
from ._input_slider import *  # noqa: F401
from ._input_text import *  # noqa: F401
from ._input_update import *  # noqa: F401
from ._insert import *  # noqa: F401
from ._markdown import *  # noqa: F401
from ._modal import *  # noqa: F401
from ._navs import *  # noqa: F401
from ._notification import *  # noqa: F401
from ._output import *  # noqa: F401
from ._page import *  # noqa: F401
from ._progress import *  # noqa: F401

from ._bootstrap import __all__ as _bootstrap_all
from ._download_button import __all__ as _download_button_all
from ._input_action_button import __all__ as _input_action_button_all
from ._input_check_radio import __all__ as _input_check_radio_all
from ._input_date import __all__ as _input_date_all
from ._input_file import __all__ as _input_file_all
from ._input_numeric import __all__ as _input_numeric_all
from ._input_password import __all__ as _input_password_all
from ._input_select import __all__ as _input_select_all
from ._input_slider import __all__ as _input_slider_all
from ._input_text import __all__ as _input_text_all
from ._input_update import __all__ as _input_update_all
from ._insert import __all__ as _insert_all
from ._modal import __all__ as _modal_all
from ._navs import __all__ as _navs_all
from ._notification import __all__ as _notification_all
from ._output import __all__ as _output_all
from ._page import __all__ as _page_all
from ._progress import __all__ as _progress_all

from htmltools import (
    TagList,
    Tag,
    TagChildArg,
    TagAttrArg,
    tags,
    HTML,
    head_content,
    p,
    h1,
    h2,
    h3,
    h4,
    h5,
    h6,
    a,
    br,
    div,
    span,
    pre,
    code,
    img,
    strong,
    em,
    hr,
)


__all__ = (
    _bootstrap_all
    + _download_button_all
    + _input_action_button_all
    + _input_check_radio_all
    + _input_date_all
    + _input_file_all
    + _input_numeric_all
    + _input_password_all
    + _input_select_all
    + _input_slider_all
    + _input_text_all
    + _input_update_all
    + _insert_all
    + _modal_all
    + _navs_all
    + _notification_all
    + _output_all
    + _page_all
    + _progress_all,
    # For some reason, if we create a tuple named `_htmltools_all` with the items below
    # and `+` that tuple here, VS Code doesn't recognize the items as being exported
    # from shiny.ui. That may be a bug in VS Code. Instead we'll just append the items
    # directly to `__all__`.
    "TagList",
    "Tag",
    "TagChildArg",
    "TagAttrArg",
    "tags",
    "HTML",
    "head_content",
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "a",
    "br",
    "div",
    "span",
    "pre",
    "code",
    "img",
    "strong",
    "em",
    "hr",
)  # pyright: ignore[reportUnsupportedDunderAll]
# pyright complains about the preceding because it only expects string literals, not
# expressions or variable names.
