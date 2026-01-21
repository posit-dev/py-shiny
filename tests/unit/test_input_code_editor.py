"""Tests for shiny/ui/_input_code_editor.py - code editor input functions."""

import warnings
from unittest.mock import MagicMock, patch

import pytest

from shiny.ui._input_code_editor import (
    CODE_EDITOR_BUNDLED_LANGUAGES,
    CODE_EDITOR_THEMES,
    LANGUAGE_ALIAS_MAP,
    SUPPORTED_LANGUAGES,
    check_value_line_count,
    code_editor_dependencies,
    code_editor_dependency,
    code_editor_dependency_prism,
    input_code_editor,
    resolve_language,
    update_code_editor,
    validate_theme,
)


# =============================================================================
# Helper: Create mock session
# =============================================================================
def create_mock_session():
    """Create a mock session object for testing code editor functions."""
    session = MagicMock()
    session._process_ui = MagicMock(side_effect=lambda x: {"html": str(x), "deps": []})
    session.send_input_message = MagicMock()
    return session


# =============================================================================
# Tests for input_code_editor
# =============================================================================
class TestInputCodeEditor:
    def test_basic_creation(self):
        """Test basic code editor creation."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor")

        html = str(tag)
        assert 'id="editor"' in html
        assert "bslib-code-editor" in html

    def test_with_label(self):
        """Test code editor with label."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", label="Code Editor")

        html = str(tag)
        assert "Code Editor" in html

    def test_with_initial_value(self):
        """Test code editor with initial value."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", value="print('hello')")

        html = str(tag)
        # Value is HTML-escaped in attributes
        assert "print(" in html or "hello" in html

    def test_with_value_as_list(self):
        """Test code editor with value as list of lines."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", value=["line1", "line2", "line3"])

        html = str(tag)
        # Lines are joined with newlines
        assert "line1" in html

    def test_language_python(self):
        """Test code editor with Python language."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="python")

        html = str(tag)
        assert 'language="python"' in html

    def test_language_javascript(self):
        """Test code editor with JavaScript language."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="javascript")

        html = str(tag)
        assert 'language="javascript"' in html

    def test_language_alias_md(self):
        """Test code editor with language alias 'md'."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="md")

        html = str(tag)
        assert 'language="markdown"' in html

    def test_language_alias_html(self):
        """Test code editor with language alias 'html'."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="html")

        html = str(tag)
        assert 'language="markup"' in html

    def test_language_plain(self):
        """Test code editor with plain language."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="plain")

        html = str(tag)
        assert 'language="plain"' in html

    def test_height_custom(self):
        """Test code editor with custom height."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", height="400px")

        html = str(tag)
        assert "400px" in html

    def test_width_custom(self):
        """Test code editor with custom width."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", width="50%")

        html = str(tag)
        assert "50%" in html

    def test_theme_light(self):
        """Test code editor with custom light theme."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", theme_light="prism")

        html = str(tag)
        assert 'theme-light="prism"' in html

    def test_theme_dark(self):
        """Test code editor with custom dark theme."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", theme_dark="dracula")

        html = str(tag)
        assert 'theme-dark="dracula"' in html

    def test_read_only_true(self):
        """Test code editor in read-only mode."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", read_only=True)

        html = str(tag)
        assert 'readonly="true"' in html

    def test_read_only_false(self):
        """Test code editor not in read-only mode."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", read_only=False)

        html = str(tag)
        assert 'readonly="false"' in html

    def test_line_numbers_true(self):
        """Test code editor with line numbers enabled."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", line_numbers=True)

        html = str(tag)
        assert 'line-numbers="true"' in html

    def test_line_numbers_false(self):
        """Test code editor with line numbers disabled."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", line_numbers=False)

        html = str(tag)
        assert 'line-numbers="false"' in html

    def test_line_numbers_default_for_markdown(self):
        """Test line numbers default to False for markdown."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="markdown")

        html = str(tag)
        assert 'line-numbers="false"' in html

    def test_line_numbers_default_for_plain(self):
        """Test line numbers default to False for plain."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", language="plain")

        html = str(tag)
        assert 'line-numbers="false"' in html

    def test_word_wrap_true(self):
        """Test code editor with word wrap enabled."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", word_wrap=True)

        html = str(tag)
        assert 'word-wrap="true"' in html

    def test_word_wrap_false(self):
        """Test code editor with word wrap disabled."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", word_wrap=False)

        html = str(tag)
        assert 'word-wrap="false"' in html

    def test_tab_size_custom(self):
        """Test code editor with custom tab size."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", tab_size=2)

        html = str(tag)
        assert 'tab-size="2"' in html

    def test_tab_size_invalid_raises(self):
        """Test code editor with invalid tab size raises error."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            with pytest.raises(ValueError, match="tab_size"):
                input_code_editor("editor", tab_size=0)

    def test_indentation_space(self):
        """Test code editor with space indentation."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", indentation="space")

        html = str(tag)
        assert 'insert-spaces="true"' in html

    def test_indentation_tab(self):
        """Test code editor with tab indentation."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", indentation="tab")

        html = str(tag)
        assert 'insert-spaces="false"' in html

    def test_fill_true(self):
        """Test code editor with fill=True."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", fill=True)

        # The fill attribute adds fill-related classes/attrs
        html = str(tag)
        assert "bslib-code-editor" in html

    def test_fill_false(self):
        """Test code editor with fill=False."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            tag = input_code_editor("editor", fill=False)

        html = str(tag)
        assert "bslib-code-editor" in html

    def test_invalid_value_type_raises(self):
        """Test code editor with invalid value type raises error."""
        with patch("shiny.ui._input_code_editor.restore_input", return_value=None):
            with pytest.raises(TypeError, match="value"):
                input_code_editor("editor", value=12345)  # type: ignore


# =============================================================================
# Tests for update_code_editor
# =============================================================================
class TestUpdateCodeEditor:
    def test_update_value(self):
        """Test update_code_editor with new value."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", value="new code", session=session)

        session.send_input_message.assert_called_once()
        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == "new code"

    def test_update_value_as_list(self):
        """Test update_code_editor with value as list."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", value=["line1", "line2"], session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["value"] == "line1\nline2"

    def test_update_label(self):
        """Test update_code_editor with new label."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", label="New Label", session=session)

        session.send_input_message.assert_called_once()

    def test_update_language(self):
        """Test update_code_editor with new language."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", language="javascript", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["language"] == "javascript"

    def test_update_theme_light(self):
        """Test update_code_editor with new light theme."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", theme_light="dracula", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["theme_light"] == "dracula"

    def test_update_theme_dark(self):
        """Test update_code_editor with new dark theme."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", theme_dark="prism", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["theme_dark"] == "prism"

    def test_update_read_only(self):
        """Test update_code_editor with read_only."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", read_only=True, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["read_only"] is True

    def test_update_line_numbers(self):
        """Test update_code_editor with line_numbers."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", line_numbers=True, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["line_numbers"] is True

    def test_update_word_wrap(self):
        """Test update_code_editor with word_wrap."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", word_wrap=True, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["word_wrap"] is True

    def test_update_tab_size(self):
        """Test update_code_editor with tab_size."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", tab_size=2, session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["tab_size"] == 2

    def test_update_indentation(self):
        """Test update_code_editor with indentation."""
        session = create_mock_session()
        with patch(
            "shiny.ui._input_code_editor.require_active_session", return_value=session
        ):
            update_code_editor("editor", indentation="tab", session=session)

        call_args = session.send_input_message.call_args
        assert call_args[0][1]["indentation"] == "tab"

    def test_update_invalid_tab_size_raises(self):
        """Test update_code_editor with invalid tab_size raises."""
        session = create_mock_session()
        with pytest.raises(ValueError, match="tab_size"):
            update_code_editor("editor", tab_size=0, session=session)

    def test_update_invalid_value_type_raises(self):
        """Test update_code_editor with invalid value type raises."""
        session = create_mock_session()
        with pytest.raises(TypeError, match="value"):
            update_code_editor("editor", value=123, session=session)  # type: ignore


# =============================================================================
# Tests for resolve_language
# =============================================================================
class TestResolveLanguage:
    def test_resolve_python(self):
        """Test resolving Python language."""
        assert resolve_language("python") == "python"

    def test_resolve_javascript(self):
        """Test resolving JavaScript language."""
        assert resolve_language("javascript") == "javascript"

    def test_resolve_alias_md(self):
        """Test resolving 'md' alias to 'markdown'."""
        assert resolve_language("md") == "markdown"

    def test_resolve_alias_html(self):
        """Test resolving 'html' alias to 'markup'."""
        assert resolve_language("html") == "markup"

    def test_resolve_alias_plain(self):
        """Test resolving 'plain' alias."""
        assert resolve_language("plain") == "plain"

    def test_resolve_alias_plaintext(self):
        """Test resolving 'plaintext' alias."""
        assert resolve_language("plaintext") == "plain"

    def test_resolve_alias_text(self):
        """Test resolving 'text' alias."""
        assert resolve_language("text") == "plain"

    def test_resolve_alias_txt(self):
        """Test resolving 'txt' alias."""
        assert resolve_language("txt") == "plain"

    def test_resolve_invalid_language_raises(self):
        """Test resolving invalid language raises error."""
        with pytest.raises(ValueError, match="Invalid language"):
            resolve_language("invalid_lang")


# =============================================================================
# Tests for check_value_line_count
# =============================================================================
class TestCheckValueLineCount:
    def test_empty_string_no_warning(self):
        """Test empty string does not warn."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_value_line_count("")
            assert len(w) == 0

    def test_small_content_no_warning(self):
        """Test small content does not warn."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_value_line_count("line1\nline2\nline3")
            assert len(w) == 0

    def test_large_content_warns(self):
        """Test 1000+ lines content warns."""
        large_content = "\n".join([f"line {i}" for i in range(1000)])
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            check_value_line_count(large_content)
            assert len(w) == 1
            assert "1000" in str(w[0].message)


# =============================================================================
# Tests for validate_theme
# =============================================================================
class TestValidateTheme:
    def test_valid_theme(self):
        """Test valid theme passes validation."""
        result = validate_theme("github-light", "theme_light")
        assert result == "github-light"

    def test_valid_dark_theme(self):
        """Test valid dark theme passes validation."""
        result = validate_theme("dracula", "theme_dark")
        assert result == "dracula"

    def test_invalid_theme_raises(self):
        """Test invalid theme raises error."""
        with pytest.raises(ValueError, match="Invalid theme_light"):
            validate_theme("invalid-theme", "theme_light")


# =============================================================================
# Tests for code_editor_dependencies
# =============================================================================
class TestCodeEditorDependencies:
    def test_dependencies_returns_list(self):
        """Test dependencies returns a list."""
        deps = code_editor_dependencies()
        assert isinstance(deps, list)
        assert len(deps) == 2

    def test_prism_dependency(self):
        """Test Prism Code Editor dependency."""
        dep = code_editor_dependency_prism()
        assert dep.name == "prism-code-editor"

    def test_bslib_dependency(self):
        """Test bslib code editor dependency."""
        dep = code_editor_dependency()
        assert dep.name == "bslib-code-editor"


# =============================================================================
# Tests for constants
# =============================================================================
class TestConstants:
    def test_bundled_languages(self):
        """Test bundled languages tuple is populated."""
        assert len(CODE_EDITOR_BUNDLED_LANGUAGES) > 0
        assert "python" in CODE_EDITOR_BUNDLED_LANGUAGES
        assert "javascript" in CODE_EDITOR_BUNDLED_LANGUAGES

    def test_themes(self):
        """Test themes tuple is populated."""
        assert len(CODE_EDITOR_THEMES) > 0
        assert "github-light" in CODE_EDITOR_THEMES
        assert "github-dark" in CODE_EDITOR_THEMES

    def test_supported_languages(self):
        """Test supported languages includes bundled and aliases."""
        assert "python" in SUPPORTED_LANGUAGES
        assert "md" in SUPPORTED_LANGUAGES  # alias
        assert "html" in SUPPORTED_LANGUAGES  # alias

    def test_language_alias_map(self):
        """Test language alias map has expected entries."""
        assert LANGUAGE_ALIAS_MAP["md"] == "markdown"
        assert LANGUAGE_ALIAS_MAP["html"] == "markup"
        assert LANGUAGE_ALIAS_MAP["plain"] == "plain"
