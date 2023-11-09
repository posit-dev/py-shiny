from __future__ import annotations

from .._app import App
from ._run import wrap_express_app

app: App


def __getattr__(name: str):
    if name == "app":
        return wrap_express_app()
    raise AttributeError(f"Module 'shiny.express.app' has no attribute '{name}'")
