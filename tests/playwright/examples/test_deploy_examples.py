import pytest
from example_apps import get_apps, reruns, validate_example
from playwright.sync_api import Page


@pytest.mark.examples
@pytest.mark.flaky(reruns=reruns, reruns_delay=1)
def test_deploy_examples(page: Page) -> None:
    [
        validate_example(page, example_app)
        for example_app in get_apps("tests/playwright/deploys")
    ]
