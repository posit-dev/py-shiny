from importlib import import_module
from types import ModuleType


class MissingReactlogError(RuntimeError):
    """The optional report renderer is unavailable."""


def require_reactlog() -> ModuleType:
    try:
        return import_module("reactlog")
    except ModuleNotFoundError as err:
        if err.name != "reactlog":
            raise
        raise MissingReactlogError(
            "Reactlog reports require the reactlog Python package. "
            "From the py-shiny checkout, install it with "
            "`uv pip install --group reactlog-dev`."
        ) from err
