from __future__ import annotations

import importlib
from pathlib import Path
from typing import Set

import pytest

from ._quartodoc_utils import load_quartodoc_sections, section_contents

root = Path(__file__).parent.parent.parent

CONTROLLER_DIR = root / "shiny/playwright/controller"
DOCS_CONFIG = root / "docs/_quartodoc-testing.yml"


def get_controller_classes() -> Set[str]:
    controller_module = importlib.import_module("shiny.playwright.controller")

    res: Set[str] = set()
    for x in dir(controller_module):
        if x.startswith("_") or x.startswith("@"):
            continue
        res.add(x)

    return res


def get_documented_controllers() -> Set[str]:
    return {
        content.split(".")[-1]
        for section in load_quartodoc_sections(DOCS_CONFIG)
        for content in section_contents(section)
        if isinstance(content, str) and content.startswith("playwright.controller.")
    }


def test_all_controllers_are_documented():
    controller_classes = get_controller_classes()
    documented_controllers = get_documented_controllers()

    missing_from_docs = controller_classes - documented_controllers
    extra_in_docs = documented_controllers - controller_classes

    error_messages: list[str] = []
    if missing_from_docs:
        missing_list = "\n".join(
            sorted(f"  - playwright.controller.{c}" for c in missing_from_docs)
        )
        error_messages.append(
            f"Controllers missing from {DOCS_CONFIG}:\n{missing_list}"
        )

    if extra_in_docs:
        extra_list = "\n".join(
            sorted(f"  - playwright.controller.{c}" for c in extra_in_docs)
        )
        error_messages.append(f"Extraneous classes in {DOCS_CONFIG}:\n{extra_list}")

    if error_messages:
        pytest.fail("\n\n".join(error_messages), pytrace=False)

    assert controller_classes, "No controller classes were found."
    assert documented_controllers, "No documented controllers were found."


DOCUMENTED_TESTING_MODULES = {
    "pytest": "shiny.pytest",
    "testserver": "shiny.testserver",
}
"""Quartodoc prefix -> module, for every testing package the config publishes."""


def get_module_exports(module: str) -> Set[str]:
    """Return the public names a module exports via `__all__`."""
    return set(importlib.import_module(module).__all__)


def get_documented_names(prefix: str) -> Set[str]:
    dotted = f"{prefix}."
    return {
        content[len(dotted) :]
        for section in load_quartodoc_sections(DOCS_CONFIG)
        for content in section_contents(section)
        if isinstance(content, str) and content.startswith(dotted)
    }


@pytest.mark.parametrize("prefix,module", sorted(DOCUMENTED_TESTING_MODULES.items()))
def test_all_testing_exports_are_documented(prefix: str, module: str):
    """
    Everything these modules export must appear in the testing API reference.

    `test_all_controllers_are_documented` covers `shiny.playwright.controller`
    only, and `test_quartodoc_configs_have_unique_contents` only rejects
    duplicates, so without this an export could ship with no published docs.
    """
    exports = get_module_exports(module)
    documented = get_documented_names(prefix)

    error_messages: list[str] = []
    if exports - documented:
        missing_list = "\n".join(
            sorted(f"  - {prefix}.{name}" for name in exports - documented)
        )
        error_messages.append(f"Exports missing from {DOCS_CONFIG}:\n{missing_list}")

    if documented - exports:
        extra_list = "\n".join(
            sorted(f"  - {prefix}.{name}" for name in documented - exports)
        )
        error_messages.append(f"Extraneous entries in {DOCS_CONFIG}:\n{extra_list}")

    if error_messages:
        pytest.fail("\n\n".join(error_messages), pytrace=False)

    assert exports, f"No `{module}` exports were found."
