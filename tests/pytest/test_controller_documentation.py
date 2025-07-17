import ast
from pathlib import Path
from typing import Set

import pytest
import yaml


class ControllerDocumentationChecker:
    """Validates that all controller classes are documented."""

    CONTROLLER_DIR = Path("shiny/playwright/controller")
    DOCS_CONFIG = Path("docs/_quartodoc-testing.yml")

    SKIP_PATTERNS = {"Base", "Container", "Label", "StyleM"}
    CONTROLLER_BASE_PATTERNS = {"Base", "Container", "Label", "StyleM", "WidthLocM"}

    def get_controller_classes(self) -> Set[str]:
        """Extract public controller class names from the controller directory."""
        controller_classes: Set[str] = set()

        for py_file in self.CONTROLLER_DIR.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            try:
                controller_classes.update(self._extract_classes_from_file(py_file))
            except Exception as e:
                pytest.fail(f"Failed to parse {py_file}: {e}")

        return controller_classes

    def _extract_classes_from_file(self, py_file: Path) -> Set[str]:
        """Extract controller classes from a Python file."""
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read())

        classes: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if self._is_controller_class(node):
                    classes.add(node.name)

        return classes

    def _is_controller_class(self, node: ast.ClassDef) -> bool:
        """Check if a class definition represents a controller."""
        class_name = node.name

        if class_name.startswith("_"):
            return False

        if any(pattern in class_name for pattern in self.SKIP_PATTERNS):
            return False

        if self._is_protocol_class(node):
            return False

        return self._has_controller_base(node)

    def _is_protocol_class(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from a Protocol."""
        return any(
            isinstance(base, ast.Name) and base.id.endswith("P") for base in node.bases
        )

    def _has_controller_base(self, node: ast.ClassDef) -> bool:
        """Check if class has controller base classes."""
        for base in node.bases:
            base_str = ast.unparse(base)

            if base_str.startswith("_"):
                return True

            if any(pattern in base_str for pattern in self.CONTROLLER_BASE_PATTERNS):
                return True

        return False

    def get_documented_controllers(self) -> Set[str]:
        """Extract controller class names from documentation config."""
        try:
            with open(self.DOCS_CONFIG, encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            pytest.fail(f"Documentation config not found: {self.DOCS_CONFIG}")
        except Exception as e:
            pytest.fail(f"Failed to parse {self.DOCS_CONFIG}: {e}")

        documented_controllers: Set[str] = set()

        for section in config.get("quartodoc", {}).get("sections", []):
            for content in section.get("contents", []):
                if isinstance(content, str) and content.startswith(
                    "playwright.controller."
                ):
                    class_name = content.split(".")[-1]
                    documented_controllers.add(class_name)

        return documented_controllers


@pytest.fixture
def checker():
    """Provide a ControllerDocumentationChecker instance."""
    return ControllerDocumentationChecker()


def test_all_controllers_are_documented(checker: ControllerDocumentationChecker):
    """Verify all controller classes have documentation entries."""
    controller_classes = checker.get_controller_classes()
    documented_controllers = checker.get_documented_controllers()

    missing_controllers = controller_classes - documented_controllers
    extra_documented = documented_controllers - controller_classes

    error_messages: list[str] = []

    if missing_controllers:
        missing_list = "\n".join(
            f"  - playwright.controller.{cls}" for cls in sorted(missing_controllers)
        )
        error_messages.append(
            f"Controller classes missing from {checker.DOCS_CONFIG}:\n{missing_list}"
        )

    if extra_documented:
        extra_list = "\n".join(
            f"  - playwright.controller.{cls}" for cls in sorted(extra_documented)
        )
        error_messages.append(f"Classes documented but not found:\n{extra_list}")

    if error_messages:
        pytest.fail("\n\n".join(error_messages))

    assert controller_classes, "No controller classes found"
    assert documented_controllers, "No documented controllers found"


def test_documented_classes_format(checker: ControllerDocumentationChecker):
    """Verify documented controller entries are valid Python identifiers."""
    documented_controllers = checker.get_documented_controllers()

    invalid_names = [name for name in documented_controllers if not name.isidentifier()]

    if invalid_names:
        pytest.fail(f"Invalid controller class names: {invalid_names}")
