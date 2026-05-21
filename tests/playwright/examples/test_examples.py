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
    skip_brand_examples_on_old_brand_yml(ex_app_path)

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


def skip_brand_examples_on_old_brand_yml(ex_app_path: str) -> None:
    """Skip brand examples when brand_yml predates the htmltools 0.7.0 fix.

    brand_yml <= 0.1.1 returns a bare ``Tag`` from
    ``BrandLogoResource.tagify()``. htmltools 0.7.0 (posit-dev/py-htmltools#105)
    tightened the ``Tagifiable`` contract to require a fully-tagified return,
    so rendering a brand logo with an old brand_yml + new htmltools raises
    ``TypeError`` at the render boundary. Drop this skip once py-shiny's
    floor for ``brand_yml`` is raised past 0.1.1 (see posit-dev/brand-yml#115).
    """
    if not ex_app_path.startswith("examples/brand/"):
        return

    from importlib.metadata import PackageNotFoundError, version

    from packaging.version import Version

    try:
        installed = Version(version("brand_yml"))
    except PackageNotFoundError:
        pytest.skip("brand_yml not installed")
        return

    min_version = Version("0.1.2")
    if installed < min_version:
        pytest.skip(
            f"brand_yml {installed} predates the htmltools 0.7.0 Tagifiable"
            f" fix; requires brand_yml >= {min_version}"
            " (posit-dev/brand-yml#115)."
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
