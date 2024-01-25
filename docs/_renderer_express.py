from __future__ import annotations

from _renderer_core import Renderer as CoreRenderer


class Renderer(CoreRenderer):
    style = "shiny-express"
    express_api = True
