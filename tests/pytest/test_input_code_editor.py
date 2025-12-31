import warnings

import pytest
from htmltools import Tag

from shiny.ui import code_editor_themes, input_code_editor, update_code_editor


class TestCodeEditorThemes:
    def test_returns_tuple_of_themes(self):
        themes = code_editor_themes()

        assert isinstance(themes, tuple)
        assert len(themes) > 0
        assert all(isinstance(t, str) for t in themes)

    def test_contains_expected_default_themes(self):
        themes = code_editor_themes()

        assert "github-light" in themes
        assert "github-dark" in themes
        assert "vs-code-light" in themes
        assert "vs-code-dark" in themes


class TestInputCodeEditorValidation:
    def test_rejects_invalid_theme_light(self):
        with pytest.raises(ValueError, match="Invalid theme_light"):
            input_code_editor("test", theme_light="invalid-theme")

    def test_rejects_invalid_theme_dark(self):
        with pytest.raises(ValueError, match="Invalid theme_dark"):
            input_code_editor("test", theme_dark="invalid-theme")

    def test_rejects_invalid_language(self):
        with pytest.raises(ValueError, match="Invalid language"):
            input_code_editor("test", language="fortran")  # type: ignore

    def test_rejects_invalid_tab_size(self):
        with pytest.raises(ValueError, match="tab_size"):
            input_code_editor("test", tab_size=0)

    def test_rejects_invalid_value_type(self):
        with pytest.raises(TypeError, match="value"):
            input_code_editor("test", value=123)  # type: ignore


class TestInputCodeEditorHtmlStructure:
    def test_generates_correct_element(self):
        editor = input_code_editor(
            "test_editor",
            value="SELECT * FROM table",
            language="sql",
        )

        assert isinstance(editor, Tag)
        assert editor.name == "bslib-code-editor"

    def test_has_correct_id(self):
        editor = input_code_editor("my_editor")
        html = str(editor)
        assert 'id="my_editor"' in html

    def test_has_correct_attributes(self):
        editor = input_code_editor(
            "test",
            value="SELECT * FROM table",
            language="sql",
        )
        html = str(editor)

        assert 'language="sql"' in html
        assert "SELECT * FROM table" in html

    def test_attaches_dependencies(self):
        editor = input_code_editor("test")
        deps = editor.get_dependencies()
        dep_names = [d.name for d in deps]

        assert "prism-code-editor" in dep_names
        assert "bslib-code-editor-js" in dep_names


class TestInputCodeEditorParameters:
    def test_handles_all_parameters(self):
        editor = input_code_editor(
            "full_editor",
            value="print('hello')",
            language="python",
            height="500px",
            width="80%",
            theme_light="vs-code-light",
            theme_dark="vs-code-dark",
            read_only=True,
            line_numbers=False,
            word_wrap=True,
            tab_size=4,
            indentation="tab",
        )

        html = str(editor)

        assert 'language="python"' in html
        assert 'theme-light="vs-code-light"' in html
        assert 'theme-dark="vs-code-dark"' in html
        assert 'readonly="true"' in html
        assert 'line-numbers="false"' in html
        assert 'word-wrap="true"' in html
        assert 'tab-size="4"' in html
        assert 'insert-spaces="false"' in html  # tab indentation

    def test_uses_correct_defaults(self):
        editor = input_code_editor("default_editor", language="r")
        html = str(editor)

        assert 'language="r"' in html
        assert 'theme-light="github-light"' in html
        assert 'theme-dark="github-dark"' in html
        assert 'readonly="false"' in html
        assert 'line-numbers="true"' in html
        assert 'word-wrap="false"' in html
        assert 'tab-size="4"' in html
        assert 'insert-spaces="true"' in html

    def test_line_numbers_default_for_markdown(self):
        editor = input_code_editor("md_editor", language="markdown")
        html = str(editor)
        assert 'line-numbers="false"' in html

    def test_line_numbers_default_for_plain(self):
        editor = input_code_editor("plain_editor", language="plain")
        html = str(editor)
        assert 'line-numbers="false"' in html

    def test_word_wrap_default_follows_line_numbers(self):
        # When line_numbers is True (default for code languages), word_wrap is False
        editor_code = input_code_editor("code", language="python")
        html_code = str(editor_code)
        assert 'line-numbers="true"' in html_code
        assert 'word-wrap="false"' in html_code

        # When line_numbers is False (default for markdown), word_wrap is True
        editor_md = input_code_editor("md", language="markdown")
        html_md = str(editor_md)
        assert 'line-numbers="false"' in html_md
        assert 'word-wrap="true"' in html_md


class TestInputCodeEditorValue:
    def test_handles_empty_value(self):
        editor = input_code_editor("empty_editor", value="")
        html = str(editor)
        assert 'value=""' in html

    def test_handles_string_value(self):
        editor = input_code_editor("string_editor", value="hello world")
        html = str(editor)
        assert "hello world" in html

    def test_handles_list_value(self):
        editor = input_code_editor("list_editor", value=["one", "two", "three"])
        # The value should be joined with newlines
        # Note: In HTML attribute, newline is encoded
        assert editor.attrs["value"] == "one\ntwo\nthree"

    def test_handles_tuple_value(self):
        editor = input_code_editor("tuple_editor", value=("line1", "line2"))
        assert editor.attrs["value"] == "line1\nline2"


class TestInputCodeEditorIndentation:
    def test_space_indentation(self):
        editor = input_code_editor("test", indentation="space")
        html = str(editor)
        assert 'insert-spaces="true"' in html

    def test_tab_indentation(self):
        editor = input_code_editor("test", indentation="tab")
        html = str(editor)
        assert 'insert-spaces="false"' in html


class TestInputCodeEditorLabel:
    def test_with_label(self):
        editor = input_code_editor("test", label="SQL Query")
        html = str(editor)

        assert "<label" in html
        assert "SQL Query" in html

    def test_without_label(self):
        editor = input_code_editor("test")
        html = str(editor)

        # Should still have the custom element
        assert "<bslib-code-editor" in html


class TestInputCodeEditorLanguages:
    def test_various_languages(self):
        languages = ["sql", "python", "r", "javascript", "markup", "css", "json"]

        for lang in languages:
            editor = input_code_editor(f"editor_{lang}", language=lang)  # type: ignore
            html = str(editor)
            assert f'language="{lang}"' in html

    def test_language_aliases(self):
        # Test that aliases are resolved correctly
        editor_md = input_code_editor("md_test", language="md")
        assert editor_md.attrs["language"] == "markdown"

        editor_html = input_code_editor("html_test", language="html")
        assert editor_html.attrs["language"] == "markup"


class TestInputCodeEditorWarnings:
    def test_warns_for_1000_lines(self):
        value_1000 = "\n".join(["line"] * 1000)
        with pytest.warns(UserWarning, match="1000 lines"):
            input_code_editor("test", value=value_1000)

    def test_warns_for_more_than_1000_lines(self):
        value_2000 = "\n".join(["line"] * 2000)
        with pytest.warns(UserWarning, match="2000 lines"):
            input_code_editor("test", value=value_2000)

    def test_no_warning_for_small_values(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            input_code_editor("test", value="line1\nline2\nline3")

    def test_no_warning_for_999_lines(self):
        value_999 = "\n".join(["line"] * 999)
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            input_code_editor("test", value=value_999)


class TestUpdateCodeEditorValidation:
    def test_rejects_invalid_language(self):
        with pytest.raises(ValueError, match="Invalid language"):
            update_code_editor("test", language="fortran")  # type: ignore

    def test_rejects_invalid_theme_light(self):
        with pytest.raises(ValueError, match="Invalid theme_light"):
            update_code_editor("test", theme_light="invalid")

    def test_rejects_invalid_theme_dark(self):
        with pytest.raises(ValueError, match="Invalid theme_dark"):
            update_code_editor("test", theme_dark="invalid")

    def test_rejects_invalid_tab_size(self):
        with pytest.raises(ValueError, match="tab_size"):
            update_code_editor("test", tab_size=0)

    def test_rejects_invalid_value_type(self):
        with pytest.raises(TypeError, match="value"):
            update_code_editor("test", value=123)  # type: ignore
