from __future__ import annotations

import ast
from pathlib import Path
from typing import Set

import pytest
import yaml

root = Path(__file__).parent.parent.parent

CONTROLLER_DIR = root / "shiny/playwright/controller"
DOCS_CONFIG = root / "docs/_quartodoc-testing.yml"
SKIP_PATTERNS = {"Base", "Container", "Label", "StyleM"}
CONTROLLER_BASE_PATTERNS = {
    "Base",
    "Container",
    "Label",
    "StyleM",
    "WidthLocM",
    "InputActionButton",
    "UiBase",
    "UiWithLabel",
    "UiWithContainer",
}


def _is_valid_controller_class(node: ast.ClassDef) -> bool:
    class_name = node.name
    base_names = {ast.unparse(base) for base in node.bases}

    return (
        not class_name.startswith("_")
        and not any(pattern in class_name for pattern in SKIP_PATTERNS)
        and not any(base.endswith("P") for base in base_names if isinstance(base, str))
        and any(
            base.startswith("_") or any(p in base for p in CONTROLLER_BASE_PATTERNS)
            for base in base_names
        )
    )


def get_controller_classes() -> Set[str]:
    classes: Set[str] = set()
    for py_file in CONTROLLER_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
            classes.update(
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef) and _is_valid_controller_class(node)
            )
        except Exception as e:
            pytest.fail(f"Failed to parse {py_file}: {e}")
    return classes


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
