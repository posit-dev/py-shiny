from __future__ import annotations

__all__ = (
    "input_code_editor",
    "update_code_editor",
)

import warnings
from typing import TYPE_CHECKING, Literal, Optional, Sequence, get_args

from htmltools import HTMLDependency, Tag, TagChild, css, tags

from .._docstring import add_example, doc_format
from .._utils import drop_none
from .._versions import bslib as bslib_version
from ..bookmark import restore_input
from ..module import resolve_id
from ..session import Session, require_active_session
from ._html_deps_shinyverse import components_dependencies
from ._input_code_editor_bundle import (
    VERSION_PRISM_CODE_EDITOR,
    CodeEditorBundledLanguage,
    CodeEditorTheme,
)
from ._utils import shiny_input_label
from .fill._fill import FILL_ITEM_ATTRS, FILLABLE_CONTAINTER_ATTRS

if TYPE_CHECKING:
    from htmltools import TagAttrValue


# Language aliases (user-friendly names -> prism grammar names)
LanguageAlias = Literal["md", "html", "plain", "plaintext", "text", "txt"]

CodeEditorLanguage = CodeEditorBundledLanguage | LanguageAlias

CodeEditorIndentation = Literal["space", "tab"]

# Runtime tuples derived from types
_CODE_EDITOR_BUNDLED_LANGUAGES: tuple[str, ...] = get_args(CodeEditorBundledLanguage)
_CODE_EDITOR_THEMES: tuple[str, ...] = get_args(CodeEditorTheme)
_LANGUAGE_ALIASES: tuple[str, ...] = get_args(LanguageAlias)
_SUPPORTED_LANGUAGES: tuple[str, ...] = (
    *_CODE_EDITOR_BUNDLED_LANGUAGES,
    *_LANGUAGE_ALIASES,
)

# Alias mapping (user-friendly names -> prism grammar names)
_LANGUAGE_ALIAS_MAP: dict[str, str] = {
    "md": "markdown",
    "html": "markup",
    "plain": "plain",
    "plaintext": "plain",
    "text": "plain",
    "txt": "plain",
}


def _resolve_language(language: str) -> str:
    """Resolve language aliases to their actual grammar names."""
    if language not in _SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Invalid language: {language!r}. "
            f"Supported languages are: {', '.join(_SUPPORTED_LANGUAGES)}"
        )
    return _LANGUAGE_ALIAS_MAP.get(language, language)


def _check_value_line_count(value: str) -> None:
    """Warn if value has 1000 or more lines."""
    if not value:
        return

    line_count = value.count("\n") + 1
    if line_count >= 1000:
        warnings.warn(
            f"Code editor value contains {line_count} lines. "
            "The editor may experience performance issues with 1,000 or more lines.",
            UserWarning,
            stacklevel=3,
        )


def _validate_theme(theme: str, param_name: str) -> str:
    """Validate that a theme name is available."""
    if theme not in _CODE_EDITOR_THEMES:
        raise ValueError(
            f"Invalid {param_name}: {theme!r}. "
            f"Available themes are: {', '.join(_CODE_EDITOR_THEMES)}"
        )
    return theme


def _code_editor_dependency_prism() -> HTMLDependency:
    """HTML dependency for prism-code-editor library."""
    return HTMLDependency(
        name="prism-code-editor",
        version=VERSION_PRISM_CODE_EDITOR,
        source={
            "package": "shiny",
            "subdir": "www/shared/prism-code-editor",
        },
        script={"src": "index.js", "type": "module"},
        stylesheet=[
            {"href": "layout.css"},
            {"href": "copy.css"},
        ],
        all_files=True,
    )


def _code_editor_dependency_js() -> HTMLDependency:
    """HTML dependency for bslib code editor binding."""
    return HTMLDependency(
        name="bslib-code-editor-js",
        version=bslib_version,
        source={
            "package": "shiny",
            "subdir": "www/shared/bslib/components",
        },
        script={"src": "code-editor.min.js", "type": "module"},
    )


def _code_editor_dependencies() -> list[HTMLDependency]:
    """Returns all HTML dependencies for code editor."""
    return [
        _code_editor_dependency_prism(),
        _code_editor_dependency_js(),
        components_dependencies(),
    ]


_doc_languages = ", ".join(f'`"{lang}"`' for lang in _SUPPORTED_LANGUAGES)
_doc_themes = ", ".join(f'"`{theme}`"' for theme in _CODE_EDITOR_THEMES)


@add_example()
@doc_format(languages=_doc_languages, themes=_doc_themes)
def input_code_editor(
    id: str,
    label: TagChild = None,
    value: str | Sequence[str] = "",
    *,
    language: CodeEditorLanguage = "plain",
    height: str = "auto",
    width: str = "100%",
    theme_light: str = "github-light",
    theme_dark: str = "github-dark",
    read_only: bool = False,
    line_numbers: Optional[bool] = None,
    word_wrap: Optional[bool] = None,
    tab_size: int = 4,
    indentation: CodeEditorIndentation = "space",
    fill: bool = True,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a code editor input.

    Creates an interactive lightweight code editor input with syntax highlighting, line
    numbers, and other basic code editing features powered by Prism Code Editor.

    The editor value is not sent to the server on every keystroke. Instead, updates are
    reflected on the server when the user moves away from the editor (blur) or when they
    press `Ctrl/Cmd + Enter`.

    Parameters
    ----------
    id
        An input ID.
    label
        An optional label for the code editor.
    value
        Initial code content. Can be a string or a sequence of strings (lines).
    language
        Programming language for syntax highlighting. Supported languages include:
        {languages}.
    height
        CSS height of the editor. Set to a specific value like `"300px"` for a
        fixed height, or `"auto"` to grow with content.
    width
        CSS width of the editor.
    theme_light
        Theme to use in light mode. Available themes include: {themes}.
    theme_dark
        Theme to use in dark mode. The editor automatically switches between
        `theme_light` and `theme_dark` when used with
        :func:`~shiny.ui.input_dark_mode`.
    read_only
        Whether the editor should be read-only.
    line_numbers
        Whether to show line numbers. Defaults to `True`, except for `"markdown"`
        and `"plain"` languages where it defaults to `False`.
    word_wrap
        Whether to wrap long lines. Defaults to `True` when `line_numbers` is
        `False`, otherwise `False`.
    tab_size
        Number of spaces per tab, defaults to `4`.
    indentation
        Type of indentation: `"space"` or `"tab"`.
    fill
        Whether the code editor should fill its container. When `True` (the
        default), the editor participates in the fillable layout system.
    **kwargs
        Additional HTML attributes for the outer container element.

    Returns
    -------
    :
        A code editor input that can be added to a UI definition.

    Notes
    -----
    ::: {{.callout-note title="Server value"}}
    A string containing the current editor content.

    Unlike text inputs that update on every keystroke, the code editor only sends
    its value to the server when the user presses `Ctrl/Cmd + Enter` or when
    the editor loses focus (blur event).
    :::

    **Keyboard Shortcuts**

    The editor supports the following keyboard shortcuts:

    * `Ctrl/Cmd + Enter`: Submit the current code to the server
    * `Ctrl/Cmd + Z`: Undo
    * `Ctrl/Cmd + Shift + Z`: Redo
    * `Tab`: Indent selection
    * `Shift + Tab`: Dedent selection

    **Themes**

    The editor automatically switches between `theme_light` and `theme_dark` when
    used with :func:`~shiny.ui.input_dark_mode`.

    See Also
    --------
    * :func:`~shiny.ui.update_code_editor`
    * :func:`~shiny.ui.input_text_area`
    """
    resolved_id = resolve_id(id)

    # Handle value as sequence of lines
    if isinstance(value, (list, tuple)):
        value = "\n".join(str(v) for v in value)
    if not isinstance(value, str):
        raise TypeError("`value` must be a string or sequence of strings")

    # Restore input for bookmarking support
    restored_value = restore_input(resolved_id, default=value)
    if isinstance(restored_value, str):
        value = restored_value
    elif restored_value is not None:
        value = str(restored_value)

    # Validate inputs
    _check_value_line_count(value)
    resolved_language = _resolve_language(language)
    _validate_theme(theme_light, "theme_light")
    _validate_theme(theme_dark, "theme_dark")

    if tab_size < 1:
        raise ValueError("`tab_size` must be a positive integer")

    if line_numbers is None:
        line_numbers = resolved_language not in ("markdown", "plain")

    if word_wrap is None:
        word_wrap = not line_numbers

    insert_spaces = indentation == "space"

    label_tag = shiny_input_label(resolved_id, label)

    editor_inner = tags.div(
        FILL_ITEM_ATTRS,
        class_="code-editor",
        style=css(display="grid"),
    )

    tag = Tag(
        "bslib-code-editor",
        {
            "id": resolved_id,
            "class": "bslib-mb-spacing",
            "style": css(height=height, width=width),
            "language": resolved_language,
            "value": value,
            "theme-light": theme_light,
            "theme-dark": theme_dark,
            "readonly": str(read_only).lower(),
            "line-numbers": str(line_numbers).lower(),
            "word-wrap": str(word_wrap).lower(),
            "tab-size": str(tab_size),
            "insert-spaces": str(insert_spaces).lower(),
            **kwargs,
        },
        FILLABLE_CONTAINTER_ATTRS,
        FILL_ITEM_ATTRS if fill else {},
        label_tag,
        editor_inner,
        *_code_editor_dependencies(),
    )

    return tag


@add_example()
def update_code_editor(
    id: str,
    *,
    label: Optional[TagChild] = None,
    value: Optional[str | Sequence[str]] = None,
    language: Optional[CodeEditorLanguage] = None,
    theme_light: Optional[str] = None,
    theme_dark: Optional[str] = None,
    read_only: Optional[bool] = None,
    line_numbers: Optional[bool] = None,
    word_wrap: Optional[bool] = None,
    tab_size: Optional[int] = None,
    indentation: Optional[CodeEditorIndentation] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Update a code editor input on the client.

    Parameters
    ----------
    id
        The input ID.
    label
        An input label.
    value
        New code content. Can be a string or sequence of strings (lines).
    language
        New programming language for syntax highlighting.
    theme_light
        New theme for light mode.
    theme_dark
        New theme for dark mode.
    read_only
        Whether the editor should be read-only.
    line_numbers
        Whether to show line numbers.
    word_wrap
        Whether to wrap long lines.
    tab_size
        Number of spaces per tab.
    indentation
        Type of indentation: `"space"` or `"tab"`.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    Note
    ----
    The input updater functions send a message to the client, telling it to change the
    settings of an input object. The messages are collected and sent after all the
    observers (including outputs) have finished running.

    The syntax of these functions is similar to the functions that created the inputs in
    the first place. For example, :func:`~shiny.ui.input_code_editor` and
    :func:`~shiny.ui.update_code_editor` take a similar set of arguments.

    Any arguments with `None` values will be ignored; they will not result in any
    changes to the input object on the client.

    See Also
    --------
    * :func:`~shiny.ui.input_code_editor`
    """
    # Validate inputs first (before requiring session)
    if value is not None:
        if isinstance(value, (list, tuple)):
            value = "\n".join(str(v) for v in value)
        if not isinstance(value, str):
            raise TypeError("`value` must be a string or sequence of strings")
        _check_value_line_count(value)

    resolved_language: Optional[str] = None
    if language is not None:
        resolved_language = _resolve_language(language)
    if theme_light is not None:
        _validate_theme(theme_light, "theme_light")
    if theme_dark is not None:
        _validate_theme(theme_dark, "theme_dark")
    if tab_size is not None and tab_size < 1:
        raise ValueError("`tab_size` must be a positive integer")

    session = require_active_session(session)

    msg = {
        "label": session._process_ui(label) if label is not None else None,
        "value": value,
        "language": resolved_language,
        "theme_light": theme_light,
        "theme_dark": theme_dark,
        "read_only": read_only,
        "line_numbers": line_numbers,
        "word_wrap": word_wrap,
        "tab_size": tab_size,
        "indentation": indentation,
    }

    session.send_input_message(id, drop_none(msg))
