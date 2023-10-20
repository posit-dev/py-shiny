from __future__ import annotations

import sys

from .._app import App
from ._run import wrap_flat_app

app: App


class ThisMod(sys.modules[__name__].__class__):
    def __getattr__(self, name: str):
        if name == "app":
            return wrap_flat_app()
        raise AttributeError(name=name)


sys.modules[__name__].__class__ = ThisMod
