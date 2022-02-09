"""Top-level package for Shiny."""

__author__ = """Winston Chang"""
__email__ = "winston@rstudio.com"
__version__ = "0.0.0.9001"

from . import ui
from . import reactive
from . import reactcore

# Submodules we _don't_ want to make available for `from shiny import *`
# (just some of their classes/functions/etc.)
from .app import *
from .decorators import *
from .input_handlers import *
from .render import *
from .session import *
from .shinymodule import *
from .validation import *

from .app import __all__ as _app_all
from .decorators import __all__ as _decorators_all
from .input_handlers import __all__ as _input_handlers_all
from .render import __all__ as _render_all
from .session import __all__ as _session_all
from .shinymodule import __all__ as _shinymodule_all
from .validation import __all__ as _validation_all

__all__ = (
    ("ui", "reactive", "reactcore")
    + _app_all
    + _decorators_all
    + _input_handlers_all
    + _render_all
    + _session_all
    + _shinymodule_all
    + _validation_all
)
