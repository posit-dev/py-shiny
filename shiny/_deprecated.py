import warnings
from typing import Any

__all__ = (
    "render_text",
    "render_plot",
    "render_image",
    "render_ui",
    "event",
)


# Create our own warning class instead of using built-in DeprecationWarning, because we
# want to be able to control display of these messages without interfering with the
# user's control of DeprecationWarning.
class ShinyDeprecationWarning(RuntimeWarning):
    pass


# By default DeprecationWarnings aren't shown; we want to always show them.
warnings.simplefilter("always", ShinyDeprecationWarning)


def warn_deprecated(message: str):
    warnings.warn(message, ShinyDeprecationWarning, stacklevel=3)


def render_text():
    """Deprecated. Please use render.text() instead of render_text()."""
    import shiny.render as render

    warn_deprecated("render_text() is deprecated. Use render.text() instead.")
    return render.text()


def render_ui():
    """Deprecated. Please use render.ui() instead of render_ui()."""
    import shiny.render as render

    warn_deprecated("render_ui() is deprecated. Use render.ui() instead.")
    return render.ui()


def render_plot(*args: Any, **kwargs: Any):  # type: ignore
    """Deprecated. Please use render.plot() instead of render_plot()."""
    import shiny.render as render

    warn_deprecated("render_plot() is deprecated. Use render.plot() instead.")
    return render.plot(*args, **kwargs)  # type: ignore


def render_image(*args: Any, **kwargs: Any):  # type: ignore
    """Deprecated. Please use render.image() instead of render_image()."""
    import shiny.render as render

    warn_deprecated("render_image() is deprecated. Use render.image() instead.")
    return render.image(*args, **kwargs)  # type: ignore


def event(*args: Any, **kwargs: Any):
    """Deprecated. Please use @reactive.event() instead of @event()."""
    import shiny.reactive as reactive

    warn_deprecated("@event() is deprecated. Use @reactive.event() instead.")
    return reactive.event(*args, **kwargs)


def session_type_warning() -> None:
    warn_deprecated(
        "`session=` is deprecated. Please call with no `session=` argument as this parameter will be removed in the near future. If you need to pass a session, use your code inside a `with session_context(session):`."
    )


_session_param_docs = """
    session
        Deprecated. If a custom :class:`~shiny.Session` is needed, please execute your
        code inside `with shiny.session.session_context(session):`. See
        :func:`~shiny.session.session_context` for more details.
    """
