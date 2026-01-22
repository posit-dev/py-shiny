"""Tests for shiny.ui._input_code_editor_bundle module."""

from typing import get_args

from shiny.ui._input_code_editor_bundle import (
    VERSION_PRISM_CODE_EDITOR,
    CodeEditorBundledLanguage,
    CodeEditorTheme,
)


class TestVersionPrismCodeEditor:
    """Tests for VERSION_PRISM_CODE_EDITOR constant."""

    def test_version_is_string(self):
        """VERSION_PRISM_CODE_EDITOR should be a string."""
        assert isinstance(VERSION_PRISM_CODE_EDITOR, str)

    def test_version_is_not_empty(self):
        """VERSION_PRISM_CODE_EDITOR should not be empty."""
        assert len(VERSION_PRISM_CODE_EDITOR) > 0

    def test_version_follows_semver_format(self):
        """VERSION_PRISM_CODE_EDITOR should follow a version format."""
        parts = VERSION_PRISM_CODE_EDITOR.split(".")
        assert len(parts) >= 3  # At least major.minor.patch


class TestCodeEditorBundledLanguage:
    """Tests for CodeEditorBundledLanguage literal type."""

    def test_code_editor_bundled_language_is_literal(self):
        """CodeEditorBundledLanguage should be a Literal type."""
        allowed_values = get_args(CodeEditorBundledLanguage)
        assert isinstance(allowed_values, tuple)
        assert len(allowed_values) > 0

    def test_contains_common_languages(self):
        """CodeEditorBundledLanguage should contain common programming languages."""
        allowed_values = get_args(CodeEditorBundledLanguage)
        expected_languages = [
            "python",
            "javascript",
            "typescript",
            "css",
            "json",
            "markdown",
            "r",
        ]
        for lang in expected_languages:
            assert lang in allowed_values

    def test_contains_markup_languages(self):
        """CodeEditorBundledLanguage should contain markup languages."""
        allowed_values = get_args(CodeEditorBundledLanguage)
        assert "xml" in allowed_values
        assert "markup" in allowed_values
        assert "yaml" in allowed_values
        assert "toml" in allowed_values

    def test_contains_systems_languages(self):
        """CodeEditorBundledLanguage should contain systems languages."""
        allowed_values = get_args(CodeEditorBundledLanguage)
        assert "bash" in allowed_values
        assert "cpp" in allowed_values
        assert "rust" in allowed_values

    def test_contains_data_languages(self):
        """CodeEditorBundledLanguage should contain data-related languages."""
        allowed_values = get_args(CodeEditorBundledLanguage)
        assert "sql" in allowed_values
        assert "julia" in allowed_values

    def test_contains_style_languages(self):
        """CodeEditorBundledLanguage should contain styling languages."""
        allowed_values = get_args(CodeEditorBundledLanguage)
        assert "sass" in allowed_values
        assert "scss" in allowed_values
        assert "css" in allowed_values


class TestCodeEditorTheme:
    """Tests for CodeEditorTheme literal type."""

    def test_code_editor_theme_is_literal(self):
        """CodeEditorTheme should be a Literal type."""
        allowed_values = get_args(CodeEditorTheme)
        assert isinstance(allowed_values, tuple)
        assert len(allowed_values) > 0

    def test_contains_atom_theme(self):
        """CodeEditorTheme should contain atom theme."""
        allowed_values = get_args(CodeEditorTheme)
        assert "atom-one-dark" in allowed_values

    def test_contains_github_themes(self):
        """CodeEditorTheme should contain github themes."""
        allowed_values = get_args(CodeEditorTheme)
        assert "github-dark" in allowed_values
        assert "github-dark-dimmed" in allowed_values
        assert "github-light" in allowed_values

    def test_contains_prism_themes(self):
        """CodeEditorTheme should contain prism themes."""
        allowed_values = get_args(CodeEditorTheme)
        assert "prism" in allowed_values
        assert "prism-okaidia" in allowed_values
        assert "prism-solarized-light" in allowed_values
        assert "prism-tomorrow" in allowed_values
        assert "prism-twilight" in allowed_values

    def test_contains_vscode_themes(self):
        """CodeEditorTheme should contain vscode themes."""
        allowed_values = get_args(CodeEditorTheme)
        assert "vs-code-dark" in allowed_values
        assert "vs-code-light" in allowed_values

    def test_contains_night_owl_themes(self):
        """CodeEditorTheme should contain night owl themes."""
        allowed_values = get_args(CodeEditorTheme)
        assert "night-owl" in allowed_values
        assert "night-owl-light" in allowed_values

    def test_contains_dracula_theme(self):
        """CodeEditorTheme should contain dracula theme."""
        allowed_values = get_args(CodeEditorTheme)
        assert "dracula" in allowed_values

    def test_all_values_are_strings(self):
        """All CodeEditorTheme values should be strings."""
        allowed_values = get_args(CodeEditorTheme)
        for value in allowed_values:
            assert isinstance(value, str)
