from __future__ import annotations

from typing import Literal, Optional

from htmltools import Tag, tags

__all__ = ("settings", "disable", "enable")


def settings(
    type: Optional[Literal["tadpole", "disc", "dots", "dot-track", "bounce"]] = None,
    color: Optional[str] = None,
    size: Optional[str] = None,
    speed: Optional[str] = None,
    delay: Optional[str] = None,
    css_selector: str = ":root",
) -> Tag:
    """
    Customize UI loading spinners.

    When supplied in your app's UI, elements that are loading (e.g. plots or tables)
    will have a spinner displayed over them. This is useful for when you have a
    long-running computation and want to indicate to the user that something is
    happening beyond the default grayed-out element.

    Parameters
    ----------

    type
        The type of spinner to use. Options include "tadpole", "disc", "dots",
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


def disable() -> Tag:
    """
    Disable loading spinners.

    Include this in your app's UI to disable the loading spinners.

    Returns
    -------
    A <script> tag.
    """

    return tags.script(
        f"(function() {{ document.body.classList.add('{DISABLE_CSS_CLASS}') }} )()"
    )


def enable() -> Tag:
    """
    Enable loading spinners.

    Include this in your app's UI to enable the loading spinners. Since spinners are
    enabled by default, this is only necessary if you've previously disabled them.

    Returns
    -------
    A <script> tag.
    """

    return tags.script(
        f"(function() {{ document.body.classList.remove('{DISABLE_CSS_CLASS}') }} )()"
    )


DISABLE_CSS_CLASS = "disable-shiny-spinners"
