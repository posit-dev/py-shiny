from __future__ import annotations

from typing import Literal

from htmltools import Tag, tags

from .._docstring import add_example, no_example

__all__ = (
    "spinner_options",
    "pulse_options",
    "use",
)


BusyType = Literal["spinners", "pulse"]


@add_example(ex_dir="../api-examples/busy_indicators")
def use(*, spinners: bool = True, pulse: bool = True) -> Tag:
    """
    Use and customize busy indicator types.

    Include the result of this function in the app's UI to customize busy indicator types.

    Parameters
    ----------
    spinners
        Overlay a spinner on each calculating/recalculating output.
    pulse
        Show a pulsing banner at the top of the window when the server is busy.

    Note
    ----
    When both `spinners` and `pulse` are set to `True`, the pulse is disabled when
    spinner(s) are active.
    When both `spinners` and `pulse` are set to `False`, no busy indication is shown
    (other than the gray-ing out of recalculating outputs).

    Returns
    -------
    :
        An HTML dependency.
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


@no_example()
def spinner_options(
    type: Literal["tadpole", "disc", "dots", "dot-track", "bounce"] | str | None = None,
    *,
    color: str | None = None,
    size: str | None = None,
    easing: str | None = None,
    speed: str | None = None,
    delay: str | None = None,
    css_selector: str = ":root",
) -> Tag:
    """
    Customize spinning busy indicators.

    Include the result of this function in the app's UI to customize spinner appearance.

    Parameters
    ----------
    type
        The type of spinner to use. Builtin options include: tadpole, disc, dots,
        dot-track, and bounce. A custom type may also provided, which should be a valid
        value for the CSS
        [mask-image](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image)
        property.
    color
        The color of the spinner. This can be any valid CSS color. Defaults to the
        app's "primary" color (if Bootstrap is on the page) or light-blue if not.
    size
        The size of the spinner. This can be any valid CSS size. Defaults to "40px".
    easing
        The easing function to use for the spinner animation. This can be any valid CSS
        [easing
        function](https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function).
        Defaults to "linear".
    speed
        The amount of time for the spinner to complete a single revolution. This can be
        any valid CSS time. Defaults to "2s".
    delay
        The amount of time to wait before showing the spinner. This can be any valid CSS
        time. Defaults to "0.3s". This is useful for not showing the spinner if the
        computation finishes quickly.
    css_selector
        A CSS selector for scoping the spinner customization. Defaults to the root
        element.

    Returns
    -------
    :
        A `<style>` tag.

    Note
    ----
    To effectively disable spinners, set the `size` to "0px".
    """

    # bounce requires a different animation than the others
    if type == "bounce":
        animation = "shiny-busy-spinner-bounce"
        speed = speed or "0.8s"
    else:
        animation = None

    # Supported types have a CSS var already defined with their SVG data
    if type in ("tadpole", "disc", "dots", "dot-track", "bounce"):
        type = f"var(--_shiny-spinner-type-{type})"

    # Options are controlled via CSS variables.
    css_vars = (
        (f"--shiny-spinner-mask-img: {type};" if type else "")
        + (f"--shiny-spinner-easing: {easing};" if easing else "")
        + (f"--shiny-spinner-animation: {animation};" if animation else "")
        + (f"--shiny-spinner-color: {color};" if color else "")
        + (f"--shiny-spinner-size: {size};" if size else "")
        + (f"--shiny-spinner-speed: {speed};" if speed else "")
        + (f"--shiny-spinner-delay: {delay};" if delay else "")
    )

    # The CSS cascade allows this to be called multiple times, and as long as the CSS
    # selector is the same, the last call takes precedence. Also, css_selector allows
    # for scoping of the spinner customization.
    return tags.style(css_selector + " {" + css_vars + "}")


@no_example()
def pulse_options(
    *,
    background: str | None = None,
    height: str | None = None,
    speed: str | None = None,
) -> Tag:
    """
    Customize the pulsing busy indicator.

    Include the result of this function in the app's UI to customize the pulsing banner

    Parameters
    ----------
    background
        A CCS background definition for the pulse. The default uses a
        [linear-gradient](https://developer.mozilla.org/en-US/docs/Web/CSS/gradient/linear-gradient)
        of the theme's indigo, purple, and pink colors.
    height
        The height of the pulsing banner. This can be any valid CSS size.

    Returns
    -------
    :
        A `<style>` tag.
    """

    css_vars = (
        (f"--shiny-pulse-background: {background};" if background else "")
        + (f"--shiny-pulse-height: {height};" if height else "")
        + (f"--shiny-pulse-speed: {speed};" if speed else "")
    )

    return tags.style(":root {" + css_vars + "}")
