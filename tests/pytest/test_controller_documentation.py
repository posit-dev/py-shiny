from __future__ import annotations

import importlib
from pathlib import Path
from typing import Set

import pytest
import yaml

root = Path(__file__).parent.parent.parent

CONTROLLER_DIR = root / "shiny/playwright/controller"
DOCS_CONFIG = root / "docs/_quartodoc-testing.yml"
QUARTODOC_CONFIGS = tuple(sorted((root / "docs").glob("_quartodoc-*.yml")))


def get_controller_classes() -> Set[str]:
    controller_module = importlib.import_module("shiny.playwright.controller")

    res: Set[str] = set()
    for x in dir(controller_module):
        if x.startswith("_") or x.startswith("@"):
            continue
        res.add(x)

    return res


def get_documented_controllers() -> Set[str]:
    try:
        config = yaml.safe_load(DOCS_CONFIG.read_text(encoding="utf-8"))
    except Exception as e:
        pytest.fail(f"Failed to load or parse {DOCS_CONFIG}: {e}")

    return {
        content.split(".")[-1]
        for section in config.get("quartodoc", {}).get("sections", [])
        for content in section.get("contents", [])
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


def _quartodoc_content_name(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        name = content.get("name") or content.get("path")
        if isinstance(name, str):
            return name
        return yaml.safe_dump(content, sort_keys=True)
    return repr(content)


def test_quartodoc_configs_have_unique_contents():
    error_messages: list[str] = []

    for config_path in QUARTODOC_CONFIGS:
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except Exception as e:
            pytest.fail(f"Failed to load or parse {config_path}: {e}")

        for section in config.get("quartodoc", {}).get("sections", []):
            seen: set[str] = set()
            duplicates: list[str] = []

            for content in section.get("contents", []):
                content_name = _quartodoc_content_name(content)
                if content_name in seen:
                    duplicates.append(content_name)
                else:
                    seen.add(content_name)

            if duplicates:
                duplicate_list = "\n".join(sorted(f"  - {x}" for x in duplicates))
                error_messages.append(
                    f"Duplicate contents in {config_path}, "
                    f"section {section.get('title')!r}:\n{duplicate_list}"
                )

    if error_messages:
        pytest.fail("\n\n".join(error_messages), pytrace=False)

    assert QUARTODOC_CONFIGS, "No Quartodoc configs were found."
