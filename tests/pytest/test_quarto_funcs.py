"""Tests for shiny.quarto module."""

import pytest

from shiny.quarto import (
    DetectImportStarVisitor,
    code_has_star_import,
    get_shiny_deps,
    placeholder_dep,
    validate_code_has_no_star_import,
)


class TestPlaceholderDep:
    """Tests for placeholder_dep function."""

    def test_placeholder_dep_returns_dict(self) -> None:
        """Test placeholder_dep returns a dictionary."""
        result = placeholder_dep()
        assert isinstance(result, dict)

    def test_placeholder_dep_has_name(self) -> None:
        """Test placeholder_dep has name field."""
        result = placeholder_dep()
        assert "name" in result
        assert result["name"] == "shiny-dependency-placeholder"

    def test_placeholder_dep_has_version(self) -> None:
        """Test placeholder_dep has version field."""
        result = placeholder_dep()
        assert "version" in result
        assert result["version"] == "9.9.9"

    def test_placeholder_dep_has_meta(self) -> None:
        """Test placeholder_dep has meta field."""
        result = placeholder_dep()
        assert "meta" in result
        assert "shiny-dependency-placeholder" in result["meta"]


class TestGetShinyDeps:
    """Tests for get_shiny_deps function."""

    def test_get_shiny_deps_returns_json(self) -> None:
        """Test get_shiny_deps returns valid JSON string."""
        import json

        result = get_shiny_deps()
        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_get_shiny_deps_contains_placeholder(self) -> None:
        """Test get_shiny_deps contains placeholder dependency."""
        result = get_shiny_deps()
        assert "shiny-dependency-placeholder" in result


class TestCodeHasStarImport:
    """Tests for code_has_star_import function."""

    def test_code_with_star_import(self) -> None:
        """Test detection of star import."""
        code = "from os import *"
        assert code_has_star_import(code) is True

    def test_code_without_star_import(self) -> None:
        """Test code without star import."""
        code = "from os import path"
        assert code_has_star_import(code) is False

    def test_code_regular_import(self) -> None:
        """Test regular import statement."""
        code = "import os"
        assert code_has_star_import(code) is False

    def test_code_multiple_imports(self) -> None:
        """Test code with multiple imports, no star."""
        code = "import os\nimport sys\nfrom pathlib import Path"
        assert code_has_star_import(code) is False

    def test_code_star_import_among_others(self) -> None:
        """Test detection of star import among other imports."""
        code = "import os\nfrom sys import *\nfrom pathlib import Path"
        assert code_has_star_import(code) is True

    def test_code_syntax_error(self) -> None:
        """Test code with syntax error returns False."""
        code = "from import * what"
        assert code_has_star_import(code) is False


class TestValidateCodeHasNoStarImport:
    """Tests for validate_code_has_no_star_import function."""

    def test_validates_without_star(self) -> None:
        """Test validation passes for code without star import."""
        code = "from os import path"
        # Should not raise
        validate_code_has_no_star_import(code)

    def test_raises_for_star_import(self) -> None:
        """Test validation raises for star import."""
        code = "from os import *"
        with pytest.raises(ValueError, match="import \\*"):
            validate_code_has_no_star_import(code)


class TestDetectImportStarVisitor:
    """Tests for DetectImportStarVisitor class."""

    def test_initial_state(self) -> None:
        """Test visitor initial state."""
        visitor = DetectImportStarVisitor()
        assert visitor.found_star_import is False

    def test_detects_star_import(self) -> None:
        """Test visitor detects star import."""
        import ast

        code = "from os import *"
        tree = ast.parse(code)
        visitor = DetectImportStarVisitor()
        visitor.visit(tree)
        assert visitor.found_star_import is True

    def test_no_star_import(self) -> None:
        """Test visitor doesn't detect regular imports."""
        import ast

        code = "from os import path"
        tree = ast.parse(code)
        visitor = DetectImportStarVisitor()
        visitor.visit(tree)
        assert visitor.found_star_import is False
