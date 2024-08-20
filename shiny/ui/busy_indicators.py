from __future__ import annotations

from base64 import b64encode
from pathlib import Path
from typing import get_args

from htmltools import TagChild, TagList, tags

from .._docstring import add_example, no_example
from .._utils import private_random_int
from ._busy_spinner_types import BusySpinnerType
from ._card import CardItem

__all__ = (
    "options",
    "use",
)


@add_example(ex_dir="../api-examples/busy_indicators")
def options(
    *,
    spinner_type: BusySpinnerType | Path | None = None,
    spinner_color: str | None = None,
    spinner_size: str | None = None,
    spinner_delay: str | None = None,
    spinner_selector: str | None = None,
    fade_opacity: float | None = None,
    fade_selector: str | None = None,
    pulse_background: str | None = None,
    pulse_height: str | None = None,
    pulse_speed: str | None = None,
) -> CardItem:
    """
    Customize spinning busy indicators.

    Busy indicators provide a visual cue to users when the server is busy calculating
    outputs or otherwise performing tasks (e.g., producing downloads). This function
    allows you to customize the appearance of those busy indicators. To apply the
    customization, include the result of this function inside the app's UI.

    Parameters
    ----------
    spinner_type
        The type of spinner. Pre-bundled types are listed in the `BusySpinnerType`
        type.

        A `Path` to a local SVG file can also be provided. The SVG should adhere
        to the following rules:
        * The SVG itself should contain the animation.
        * It should avoid absolute sizes (the spinner's containing DOM element size is
            set in CSS by `spinner_size`, so it should fill that container).
        * It should avoid setting absolute colors (the spinner's containing DOM
            element color is set in CSS by `spinner_color`, so it should inherit that
            color).
    spinner_color
        The color of the spinner. This can be any valid CSS color. Defaults to the
        app's "primary" color (if Bootstrap is on the page).
    spinner_size
        The size of the spinner. This can be any valid CSS size.
    spinner_delay
        The amount of time to wait before showing the spinner. This can be any valid
        CSS time and can useful for not showing the spinner if the computation
        finishes quickly.
    spinner_selector
        A character string containing a CSS selector for scoping the spinner
        customization. The default (`None`) will apply the spinner customization to the
        parent element of the spinner.
    fade_opacity
        The opacity (a number between 0 and 1) for recalculating output. Set to 1 to
        "disable" the fade.
    fade_selector
        A string containing a CSS selector for scoping the fade customization. The
        default (`None`) applies the fade customization to the parent element.
    pulse_background
        A CCS background definition for the pulse. The default uses a
        [linear-gradient](https://developer.mozilla.org/en-US/docs/Web/CSS/gradient/linear-gradient)
        of the theme's indigo, purple, and pink colors.
    pulse_height
        The height of the pulsing banner. This can be any valid CSS size.
    pulse_speed
        The speed of the pulsing banner. This can be any valid CSS time.

    See Also
    --------
    * :func:`~shiny.ui.busy_indicators.use` for enabling/disabling busy indicators.
    """

    res = TagList(
        spinner_options(
            type=spinner_type,
            color=spinner_color,
            size=spinner_size,
            delay=spinner_delay,
            selector=spinner_selector,
        ),
        fade_options(opacity=fade_opacity, selector=fade_selector),
        pulse_options(
            background=pulse_background,
            height=pulse_height,
            speed=pulse_speed,
        ),
    )

    return CardItem(res)


def spinner_options(
    *,
    type: BusySpinnerType | Path | None = None,
    color: str | None = None,
    size: str | None = None,
    delay: str | None = None,
    selector: str | None = None,
) -> TagChild:
    if (
        type is None
        and color is None
        and size is None
        and delay is None
        and selector is None
    ):
        return None

    url = None
    if type is not None:
        if isinstance(type, Path):
            with open(type, "rb") as f:
                type64 = b64encode(f.read()).decode()
                url = f"url('data:image/svg+xml;base64,{type64}')"
        else:
            if type not in get_args(BusySpinnerType):
                raise ValueError(f"Invalid spinner type: {type}")
            url = f"url('spinners/{type}.svg')"

    css_vars = (
        (f"--shiny-spinner-url: {url};" if url else "")
        + (f"--shiny-spinner-color: {color};" if color else "")
        + (f"--shiny-spinner-size: {size};" if size else "")
        + (f"--shiny-spinner-delay: {delay};" if delay else "")
    )

    id = None
    if selector is None:
        id = f"spinner-options-{private_random_int(1000, 1000000)}"
        selector = f":has(> #{id})"

    return tags.style(f"{selector} {{ {css_vars} }}", id=id)


def pulse_options(
    *,
    background: str | None = None,
    height: str | None = None,
    speed: str | None = None,
) -> TagChild:
    if background is None and height is None and speed is None:
        return None

    css_vars = (
        (f"--shiny-pulse-background: {background};" if background else "")
        + (f"--shiny-pulse-height: {height};" if height else "")
        + (f"--shiny-pulse-speed: {speed};" if speed else "")
    )

    return tags.style(":root {" + css_vars + "}")


def fade_options(
    *,
    opacity: float | None = None,
    selector: str | None = None,
) -> TagChild:
    if opacity is None and selector is None:
        return None

    css_vars = f"--shiny-fade-opacity: {opacity};" if opacity else ""

    id = None
    if selector is None:
        id = f"fade-options-{private_random_int(1000, 1000000)}"
        selector = f":has(> #{id})"

    return tags.style(f"{selector} {{ {css_vars} }}", id=id)


@no_example()
def use(*, spinners: bool = True, pulse: bool = True, fade: bool = True) -> TagList:
    """
    Enable/disable busy indication

    Busy indicators provide a visual cue to users when the server is busy calculating
    outputs or otherwise performing tasks (e.g., producing downloads). When enabled
    (they are by default), a spinner is shown on each calculating/recalculating output,
    and a pulsing banner is shown at the top of the page when the app is otherwise busy.
    To disable, include the result of this function in anywhere in the app's UI.

    Parameters
    ----------
    spinners
        Whether to show a spinner on each calculating/recalculating output.
    pulse
        Whether to show a pulsing banner at the top of the page when the app is
        busy.
    fade
        Whether to fade recalculating outputs. A value of `False` is equivalent to
        `shiny.ui.busy_indicators.options(fade_opacity=1)`.

    Note
    ----
    When both `spinners` and `pulse` are set to `True`, the pulse is disabled when
    spinner(s) are active.
    When both `spinners` and `pulse` are set to `False`, no busy indication is shown
    (other than the gray-ing out of recalculating outputs).

    See Also
    --------
    * :func:`~shiny.ui.busy_indicators.options` for customizing busy indicators.
    """

    # TODO: it'd be nice if htmltools had something like a page_attrs() that allowed us
    # to do this without needing to inject JS into the head.
    attrs = {"shinyBusySpinners": spinners, "shinyBusyPulse": pulse}
    js = ""
    for key, value in attrs.items():
        if value:
            js += f"document.documentElement.dataset.{key} = true;"
        else:
            js += f"delete document.documentElement.dataset.{key};"

    return TagList(
        tags.script(js),
        None if fade else fade_options(opacity=1),
    )
