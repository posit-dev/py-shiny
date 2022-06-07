import warnings
from typing import Any

from . import render

__all__ = (
    "render_text",
    "render_plot",
    "render_image",
    "render_ui",
)

# Create our own warning class instead of using built-in DeprecationWarning, because we
# want to be able to control display of these messages without interfering with the
# user's control of DeprecationWarning.
class ShinyDeprecationWarning(RuntimeWarning):
    pass


# By default DeprecationWarnings aren't shown; we want to always show them.
warnings.simplefilter("always", ShinyDeprecationWarning)


def _warn_deprecated(message: str):
    warnings.warn(message, ShinyDeprecationWarning)


# ======================================================================================
# Render functions
# ======================================================================================
def render_text():
    _warn_deprecated("render_text() is deprecated. Use render.text() instead.")
    return render.text()


def render_ui():
    _warn_deprecated("render_ui() is deprecated. Use render.ui() instead.")
    return render.ui()


def render_plot(*args: Any, **kwargs: Any):
    _warn_deprecated("render_plot() is deprecated. Use render.plot() instead.")
    return render.plot(*args, **kwargs)


def render_image(*args: Any, **kwargs: Any):
    _warn_deprecated("render_image() is deprecated. Use render.image() instead.")
    return render.image(*args, **kwargs)
