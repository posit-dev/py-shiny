import pytest
from example_apps import get_apps, reruns, reruns_delay, validate_example
from playwright.sync_api import Page


@pytest.mark.flaky(reruns=reruns, reruns_delay=reruns_delay)
@pytest.mark.parametrize("ex_app_path", get_apps("examples"))
def test_examples(page: Page, ex_app_path: str) -> None:
    validate_example(page, ex_app_path)
