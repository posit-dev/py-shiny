from __future__ import annotations

from typing import Literal, Optional

from htmltools import HTMLDependency

from .. import __version__


def use_loading_spinners(
    type: Literal["tadpole", "disc", "dots", "dot-track", "bounce"] = "tadpole",
    color: Optional[str] = None,
    size: Optional[str] = None,
    speed: Optional[str] = None,
    delay: Optional[str] = None,
    page_level: Optional[bool] = None,
) -> HTMLDependency:
    """
    Use spinners to indicate when an element is loading.

    When supplied in your app's UI, elements that are loading (e.g. plots or tables)
    will have a spinner displayed over them. This is useful for when you have a
    long-running computation and want to indicate to the user that something is
    happening beyond the default grayed-out element.

    Parameters
    ----------

    type
        The type of spinner to use. Options include "disc", "tadpole", "dots",
        "dot-track", and "bounce". Defaults to "tadpole".
    color
        The color of the spinner. This can be any valid CSS color. Defaults to the
        current app "primary" color (if using a theme) or light-blue if not.
    size
        The size of the spinner. This can be any valid CSS size. Defaults to "80px".
    speed
        The amount of time for the spinner to complete a single revolution. This can be
        any valid CSS time. Defaults to "1s".
    delay
        The amount of time to wait before showing the spinner. This can be any valid CSS
        time. Defaults to "0.5s". This is useful for not showing the spinner if the
        computation finishes quickly.
    page_level
        Should the spinner be shown at the page level (i.e. one spinner per app) or at
        the level of each output (default).

    Returns
    -------
    :
        An HTMLDependency that can be included in your app's UI to enable loading
        spinners.

    Notes
    -----
    This function is meant to be called a single time. If it is called multiple times
    with different arguments then only the first call will be reflected.
    """

    animation = None
    easing = None
    # Some of the spinners work better with linear easing and some with ease-in-out so
    # we modify them together.
    if type == "disc":
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
    else:
        svg = "tadpole-spinner.svg"
        easing = "linear"

    # We set options using css variables. Here we create the rule that updates the
    # appropriate variables before being included in the head of the document with our
    # html dep.
    rule_contents = (
        f"--shiny-spinner-svg: url({svg});"
        + (f"--shiny-spinner-easing: {easing};" if easing else "")
        + (f"--shiny-spinner-animation: {animation};" if animation else "")
        + (f"--shiny-spinner-color: {color};" if color else "")
        + (f"--shiny-spinner-size: {size};" if size else "")
        + (f"--shiny-spinner-speed: {speed};" if speed else "")
        + (f"--shiny-spinner-delay: {delay};" if delay else "")
    )

    dynamic_styles = (
        "<style>body:has(.recalculating){" + rule_contents + "}</style>"
        if page_level
        else "<style>.recalculating{" + rule_contents + "}</style>"
    )

    return HTMLDependency(
        "shiny-loading-spinners-css",
        version=__version__,
        source={
            "package": "shiny",
            "subdir": "www/shared/loading-spinners/",
        },
        stylesheet=[
            {"href": "spinners-page-level.css"}
            if page_level
            else {"href": "spinners-element-level.css"},
            {"href": "spinners-common.css"},
        ],
        all_files=True,
        head=dynamic_styles,
    )
