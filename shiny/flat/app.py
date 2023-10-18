from __future__ import annotations

import os
from pathlib import Path

from .. import render, ui
from .._app import App
from .._flat import flat_run
from ..session import Inputs, Outputs, Session


def app(file: Path | None = None) -> App:
    """Wrap a flat Shiny app into a Shiny `App` object.

    Parameters
    ----------
    file
        The path to the file containing the flat Shiny application. If `None`, the
        `SHINY_APP_FILE` environment variable is used.

    Returns
    -------
    :
        A `shiny.App` object.
    """
    if file is None:
        app_file = os.getenv("SHINY_APP_FILE")
        if app_file is None:
            raise ValueError(
                "No app file was specified and the SHINY_APP_FILE environment variable "
                "is not set."
            )
        file = Path(os.getcwd()) / app_file

    # TODO: title and lang
    app_ui = ui.page_fluid(ui.output_ui("__page__", style="display: contents;"))

    def flat_server(input: Inputs, output: Outputs, session: Session):
        dyn_ui = flat_run(file)

        @render.ui
        def __page__():
            return dyn_ui

    app = App(app_ui, flat_server)

    return app
