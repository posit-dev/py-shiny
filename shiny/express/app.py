from __future__ import annotations

import importlib


# If someone requests shiny.express.app:_2f_path_2f_to_2f_app_2e_py, then we will call
# wrap_express_app(Path("/path/to/app.py")) and return the result.
def __getattr__(name: str) -> object:
    app_module = importlib.import_module("shiny_express_app" + name)
    return app_module.app
