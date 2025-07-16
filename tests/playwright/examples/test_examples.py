import sys

import pytest
from example_apps import get_apps, reruns, reruns_delay, validate_example
from playwright.sync_api import Page

is_windows = sys.platform.startswith("win")


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("ex_app_path", get_apps("examples"))
def test_examples(page: Page, ex_app_path: str) -> None:

    skip_on_windows_with_timezonefinder(ex_app_path)
    skip_airmass_on_3_9(ex_app_path)

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


def skip_airmass_on_3_9(ex_app_path: str) -> None:
    print(ex_app_path)
    if ex_app_path != "examples/airmass/app.py":
        return

    import sys

    if sys.version_info[:2] != (3, 9):
        return

    try:
        # Astropy loads `numpy` at run time
        import astropy.coordinates as _  # pyright: ignore # noqa: F401
        import astropy.units as __  # pyright: ignore # noqa: F401

        # Future proofing: if astropy is _actually_ loading, raise an error
        raise RuntimeError(
            "This code believes astropy and numpy have difficulty loading on python 3.9. Please remove this check if it is no longer true."
        )
    except AttributeError as e:
        if "numpy" in str(e) and "product" in str(e):
            pytest.skip(
                "astropy and numpy has difficulty loading on python 3.9. Skipping example app: airmass. posit-dev/py-shiny#1678"
            )
            return

        # Future proofing: if the error is not what we expect, raise it
        raise e
