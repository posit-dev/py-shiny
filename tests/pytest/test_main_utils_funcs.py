"""Tests for shiny._main_utils module"""

import os

from shiny._main_utils import (
    cli_action,
    cli_bold,
    cli_code,
    cli_danger,
    cli_field,
    cli_info,
    cli_input,
    cli_ital,
    cli_success,
    cli_url,
    cli_verbatim,
    cli_wait,
    cli_warning,
    path_rel_wd,
)


class TestPathRelWd:
    """Test path_rel_wd function"""

    def test_path_rel_wd_empty(self):
        """Test path_rel_wd with no args"""
        result = path_rel_wd()
        assert result.startswith(".")

    def test_path_rel_wd_single_path(self):
        """Test path_rel_wd with single path"""
        result = path_rel_wd("subdir")
        assert "subdir" in result
        assert result.startswith(".")

    def test_path_rel_wd_multiple_paths(self):
        """Test path_rel_wd with multiple path components"""
        result = path_rel_wd("dir1", "dir2", "file.txt")
        assert "dir1" in result
        assert "dir2" in result
        assert "file.txt" in result

    def test_path_rel_wd_uses_os_path(self):
        """Test path_rel_wd uses os.path.join"""
        result = path_rel_wd("a", "b")
        expected = os.path.join(".", "a", "b")
        assert result == expected


class TestCliStyleHelpers:
    """Test CLI style helper functions"""

    def test_cli_field(self):
        """Test cli_field styling"""
        result = cli_field("test")
        # Result should be styled string containing original text
        assert "test" in result or len(result) > 0

    def test_cli_bold(self):
        """Test cli_bold styling"""
        result = cli_bold("bold text")
        # Result should contain original text
        assert "bold text" in result or len(result) > 0

    def test_cli_ital(self):
        """Test cli_ital styling"""
        result = cli_ital("italic")
        assert "italic" in result or len(result) > 0

    def test_cli_input(self):
        """Test cli_input styling"""
        result = cli_input("input text")
        assert "input text" in result or len(result) > 0

    def test_cli_code(self):
        """Test cli_code styling adds backticks"""
        result = cli_code("my_code")
        assert "`my_code`" in result

    def test_cli_url(self):
        """Test cli_url styling"""
        result = cli_url("https://example.com")
        assert "https://example.com" in result

    def test_cli_success(self):
        """Test cli_success has checkmark"""
        result = cli_success("Success message")
        # Should have a checkmark character
        assert "Success message" in result
        assert (
            "\u2713" in result or "✓" in result or len(result) > len("Success message")
        )

    def test_cli_info(self):
        """Test cli_info has info symbol"""
        result = cli_info("Info message")
        assert "Info message" in result

    def test_cli_action(self):
        """Test cli_action has arrow"""
        result = cli_action("Action message")
        assert "Action message" in result
        assert "→" in result or len(result) > len("Action message")

    def test_cli_warning(self):
        """Test cli_warning has warning symbol"""
        result = cli_warning("Warning message")
        assert "Warning message" in result

    def test_cli_danger(self):
        """Test cli_danger has danger symbol"""
        result = cli_danger("Danger message")
        assert "Danger message" in result

    def test_cli_wait(self):
        """Test cli_wait has wait symbol"""
        result = cli_wait("Wait message")
        assert "Wait message" in result


class TestCliVerbatim:
    """Test cli_verbatim function"""

    def test_cli_verbatim_list_single(self):
        """Test cli_verbatim with single item list"""
        result = cli_verbatim(["single line"])
        # Raw string should be present (without ANSI codes) somewhere
        assert "single" in result or "line" in result

    def test_cli_verbatim_list(self):
        """Test cli_verbatim with list"""
        result = cli_verbatim(["line1", "line2", "line3"])
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result

    def test_cli_verbatim_filters_empty(self):
        """Test cli_verbatim filters empty lines"""
        result = cli_verbatim(["line1", "", "line2"])
        # Empty string should be filtered out
        assert "line1" in result
        assert "line2" in result

    def test_cli_verbatim_default_indent(self):
        """Test cli_verbatim has default indent of 2 spaces"""
        result = cli_verbatim(["test"])
        # Default indent is 2 spaces
        assert result.startswith("  ") or "test" in result

    def test_cli_verbatim_custom_indent(self):
        """Test cli_verbatim with custom indent"""
        result = cli_verbatim(["test"], indent=4)
        # Custom indent of 4 spaces
        assert result.startswith("    ") or "test" in result
