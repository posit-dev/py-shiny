from __future__ import annotations

__all__ = ("input_dark_mode", "update_dark_mode")

from typing import Literal, Optional

from htmltools import Tag, TagAttrValue, css

from .._docstring import add_example, no_example
from .._namespaces import resolve_id
from ..session import Session, require_active_session
from ._web_component import web_component

BootstrapColorMode = Literal["light", "dark"]


@add_example()
def input_dark_mode(
    *,
    id: Optional[str] = None,
    mode: Optional[BootstrapColorMode] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Creates a dark mode switch input that toggles the app between dark and light modes.

    Parameters
    ----------
    id
        An optional ID for the dark mode switch. When included, the current color mode
        is reported in the value of the input with this ID.
    mode
        The initial mode of the dark mode switch. By default or when set to `None`, the
        user's system settings for the preferred color scheme will be used. Otherwise,
        set to `"light"` or `"dark"` to force the initial mode.
    **kwargs
        Additional attributes to be added to the dark mode switch, such as `class_` or
        `style`.

    Returns
    -------
    :
        A dark mode toggle switch UI element.

    References
    ----------
    * <https://getbootstrap.com/docs/5.3/customize/color-modes>
    """

    if mode is not None:
        mode = validate_dark_mode_option(mode)

    if id is not None:
        id = resolve_id(id)

    return web_component(
        "bslib-input-dark-mode",
        id=id,
        attribute="data-bs-theme",
        mode=mode,
        style=css(
            **{
                "--text-1": "var(--bs-emphasis-color)",
                "--text-2": "var(--bs-tertiary-color)",
                # TODO: Fix the vertical correction to work better with Bootstrap
                "--vertical-correction": " ",
            }
        ),
        **kwargs,
    )


def validate_dark_mode_option(mode: BootstrapColorMode) -> BootstrapColorMode:
    if mode not in ("light", "dark"):
        raise ValueError("`mode` must be either 'light' or 'dark'.")
    return mode


@no_example()
def update_dark_mode(
    mode: BootstrapColorMode, *, session: Optional[Session] = None
) -> None:
    session = require_active_session(session)

    mode = validate_dark_mode_option(mode)

    msg: dict[str, object] = {
        "method": "toggle",
        "value": mode,
    }
    session._send_message_sync({"custom": {"bslib.toggle-dark-mode": msg}})
