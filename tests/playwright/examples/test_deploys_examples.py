import pytest
from example_apps import get_apps, reruns, validate_example
from playwright.sync_api import Page


@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
@pytest.mark.parametrize("ex_app_path", get_apps("tests/playwright/deploys"))
def test_deploy_examples(page: Page, ex_app_path: str) -> None:
    validate_example(page, ex_app_path)
