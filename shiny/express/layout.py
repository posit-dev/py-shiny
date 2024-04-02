import warnings

from . import ui

warnings.warn(
    "shiny.express.layout has been deprecated and renamed to shiny.express.ui. "
    "Please import shiny.express.ui instead of shiny.express.layout.",
    ImportWarning,
    stacklevel=2,
)


def __getattr__(name: str) -> object:
    return getattr(ui, name)
