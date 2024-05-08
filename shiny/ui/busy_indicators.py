from __future__ import annotations

from htmltools import Tag, TagChild, TagList, tags

from .._docstring import add_example, no_example

__all__ = (
    "options",
    "use",
)


@add_example(ex_dir="../api-examples/busy_indicators")
def options(
    *,
    spinner_color: str | None = None,
    spinner_size: str | None = None,
    spinner_delay: str | None = None,
    pulse_background: str | None = None,
    pulse_height: str | None = None,
    pulse_speed: str | None = None,
) -> TagList:
    """
    Customize spinning busy indicators.

    Include the result of this function in the app's UI to customize spinner appearance.

    Parameters
    ----------
    spinner_color
        The color of the spinner. This can be any valid CSS color. Defaults to the
        app's "primary" color (if Bootstrap is on the page).
    spinner_size
        The size of the spinner. This can be any valid CSS size.
    spinner_delay
        The amount of time to wait before showing the spinner. This can be any valid
        CSS time and can useful for not showing the spinner if the computation
        finishes quickly.
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

    return TagList(
        spinner_options(
            color=spinner_color,
            size=spinner_size,
            delay=spinner_delay,
        ),
        pulse_options(
            background=pulse_background,
            height=pulse_height,
            speed=pulse_speed,
        ),
    )


def spinner_options(
    *,
    color: str | None = None,
    size: str | None = None,
    delay: str | None = None,
) -> TagChild:
    if color is None and size is None and delay is None:
        return None

    css_vars = (
        (f"--shiny-spinner-color: {color};" if color else "")
        + (f"--shiny-spinner-size: {size};" if size else "")
        + (f"--shiny-spinner-delay: {delay};" if delay else "")
    )

    return tags.style(":root {" + css_vars + "}")


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


@no_example()
def use(*, spinners: bool = True, pulse: bool = True) -> Tag:
    """
    Enable/disable busy indication

    To enable/disable busy indicators, include the result of this function in the
    app's UI.

    Parameters
    ----------
    spinners
        Whether to show a spinner on each calculating/recalculating output.
    pulse
        Whether to show a pulsing banner at the top of the page when the app is
        busy.

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

    return tags.script(js)
