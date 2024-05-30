from __future__ import annotations

import logging
import sys
from pathlib import PurePath
from typing import Literal, Union

import pytest

from .._conftest import run_shiny_app

__all__ = (
    "create_app_fixture",
    "local_app_fixture_gen",
    "ScopeName",
)


# Attempt up to 3 times to start the app, with a random port each time
def local_app_fixture_gen(app: PurePath | str):
    """
    Generate a local Shiny app fixture.

    Parameters
    ----------
    app
        The path to the Shiny app file.
    """

    has_yielded_app = False
    remaining_attempts = 3
    while not has_yielded_app and remaining_attempts > 0:
        remaining_attempts -= 1

        # Make shiny process
        sa = run_shiny_app(app, wait_for_start=False, port=0)
        try:
            # enter / exit shiny context manager; (closes streams on exit)
            with sa:
                # Wait for shiny app to start
                # Could throw a `ConnectionError` if the port is already in use
                sa.wait_until_ready(30)
                # Run app!
                has_yielded_app = True
                yield sa
        except ConnectionError as e:
            if remaining_attempts == 0:
                # Ran out of attempts!
                raise e
            print(f"Failed to bind to port: {e}", file=sys.stderr)
            # Try again with a new port!
        finally:
            if has_yielded_app:
                logging.warning("Application output:\n" + str(sa.stderr))


ScopeName = Literal["session", "package", "module", "class", "function"]


def create_app_fixture(
    app: Union[PurePath, str],
    scope: ScopeName = "module",
):
    """
    Create a fixture for a local Shiny app directory.

    Parameters
    ----------
    app
        The path to the Shiny app file.
    scope
        The scope of the fixture.
    """

    @pytest.fixture(scope=scope)
    def fixture_func():
        app_gen = local_app_fixture_gen(app)
        yield next(app_gen)

    return fixture_func
