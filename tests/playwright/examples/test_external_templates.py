import sys
from pathlib import Path

import pytest
from conftest import here_root
from example_apps import get_apps, reruns, reruns_delay, validate_example
from playwright.sync_api import Page

if not Path(here_root / "py-shiny-templates").exists():
    pytest.skip(
        "./py-shiny-templates dir is not available. Skipping test.",
        allow_module_level=True,
    )


@pytest.mark.skipif(
    sys.version_info[:2] == (3, 9),
    reason="Skipping test for Python 3.9 since scikit-learn pinned version is only supported on Python 3.10+",
)
@pytest.mark.only_browser("chromium")
@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("ex_app_path", get_apps("py-shiny-templates"))
def test_external_templates(page: Page, ex_app_path: str) -> None:
    validate_example(page, ex_app_path)
