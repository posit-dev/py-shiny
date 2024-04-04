from __future__ import annotations

from typing import Literal

from htmltools import Tag, tags

__all__ = ("mode", "spinner_options")


def mode(type: Literal["spinners", "cursor", "none"] = "spinners") -> Tag:
    if type not in ("spinners", "cursor", "none"):
        raise ValueError(f"Invalid loading indicator mode: {type}")

    return tags.script(
        f"$(function() {{ document.body.dataset.shinyLoadingIndicatorMode = '{type}'; }});"
    )


def spinner_options(
    type: Literal["tadpole", "disc", "dots", "dot-track", "bounce"] | None = None,
    color: str | None = None,
    size: str | None = None,
    speed: str | None = None,
    delay: str | None = None,
    css_selector: str = ":root",
) -> Tag:
    """
    Customize UI loading indicators applied to recalculating outputs.

    Parameters
    ----------

    type
        The type of  to use. Options include "tadpole", "disc", "dots",
        "dot-track", and "bounce". Defaults to "tadpole".
    color
        The color of the spinner. This can be any valid CSS color. Defaults to the
        current app "primary" color (if using a theme) or light-blue if not.
    size
        The size of the spinner. This can be any valid CSS size. Defaults to "40px".
    speed
        The amount of time for the spinner to complete a single revolution. This can be
        any valid CSS time. Defaults to "2s".
    delay
        The amount of time to wait before showing the spinner. This can be any valid CSS
        time. Defaults to "0.1s". This is useful for not showing the spinner if the
        computation finishes quickly.
    css_selector
        A CSS selector for scoping the spinner customization. Defaults to the root element.

    Returns
    -------
     A <style> tag.
    """

    animation = None
    easing = None
    svg = None

    # Some of the spinners work better with linear easing and some with ease-in-out so
    # we modify them together.
    if type == "tadpole":
        svg = "tadpole-spinner.svg"
        easing = "linear"
    elif type == "disc":
        svg = "disc-spinner.svg"
        easing = "linear"
    elif type == "dots":
        svg = "dots-spinner.svg"
        easing = "linear"
    elif type == "dot-track":
        svg = "dot-track-spinner.svg"
        easing = "linear"
    elif type == "bounce":
        svg = "ball.svg"
        animation = "shiny-loading-spinner-bounce"
        # Set speed variable to 0.8s if it hasnt been set by the user
        speed = speed or "0.8s"
    elif type is not None:
        raise ValueError(f"Invalid spinner type: {type}")

    # Options are controlled via CSS variables. Note that the cascade allows this to be
    # called multiple times. As long as the CSS selector is the same, the last call
    # takes precedence. Also, css_selector allows for scoping of the spinner customization.
    css_vars = (
        (f"--shiny-spinner-svg: url({svg});" if svg else "")
        + (f"--shiny-spinner-easing: {easing};" if easing else "")
        + (f"--shiny-spinner-animation: {animation};" if animation else "")
        + (f"--shiny-spinner-color: {color};" if color else "")
        + (f"--shiny-spinner-size: {size};" if size else "")
        + (f"--shiny-spinner-speed: {speed};" if speed else "")
        + (f"--shiny-spinner-delay: {delay};" if delay else "")
    )

    return tags.style(css_selector + " {" + css_vars + "}")
