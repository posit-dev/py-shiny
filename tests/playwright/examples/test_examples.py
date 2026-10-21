import sys

import pytest
from example_apps import get_apps, reruns, reruns_delay, validate_example
from playwright.sync_api import Page

is_windows = sys.platform.startswith("win")


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("ex_app_path", get_apps("examples"))
def test_examples(page: Page, ex_app_path: str) -> None:

    skip_on_windows_with_timezonefinder(ex_app_path)

    validate_example(page, ex_app_path)


def skip_on_windows_with_timezonefinder(ex_app_path: str) -> None:
    if not is_windows:
        return
    if ex_app_path != "examples/airmass/app.py":
        return

    try:
        import timezonefinder  # noqa: F401 # pyright: ignore

        # Future proofing: if timezonefinder is actually available on windows, raise an error
        raise RuntimeError(
            "This code believes timezonefinder is not available on windows. Please remove this check if it is no longer true."
        )
    except ImportError:
        pytest.skip(
            "timezonefinder has difficulty compiling on windows. Skipping example app. posit-dev/py-shiny#1651"
        )
