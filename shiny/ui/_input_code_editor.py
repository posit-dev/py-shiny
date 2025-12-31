from __future__ import annotations

__all__ = (
    "input_code_editor",
    "update_code_editor",
    "code_editor_themes",
)

import warnings
from typing import TYPE_CHECKING, Literal, Optional, Sequence

from htmltools import HTMLDependency, Tag, TagChild, css, tags

from .._docstring import add_example
from .._utils import drop_none
from .._versions import bslib as bslib_version
from ..bookmark import restore_input
from ..module import resolve_id
from ..session import Session, require_active_session
from ._html_deps_shinyverse import components_dependencies
from ._utils import shiny_input_label

if TYPE_CHECKING:
    from htmltools import TagAttrValue


# Bundled languages from prism-code-editor (from bslib's R/versions.R)
CODE_EDITOR_BUNDLED_LANGUAGES: tuple[str, ...] = (
    "r",
    "python",
    "julia",
    "sql",
    "javascript",
    "typescript",
    "markup",
    "css",
    "scss",
    "sass",
    "json",
    "markdown",
    "yaml",
    "xml",
    "toml",
    "ini",
    "bash",
    "docker",
    "latex",
    "cpp",
    "rust",
    "diff",
)

# Language aliases (user-friendly names -> prism grammar names)
_LANGUAGE_ALIASES: dict[str, str] = {
    "md": "markdown",
    "html": "markup",
    "plain": "plain",
    "plaintext": "plain",
    "text": "plain",
    "txt": "plain",
}

# All supported languages: bundled prism grammars + aliases
_SUPPORTED_LANGUAGES: tuple[str, ...] = (
    *CODE_EDITOR_BUNDLED_LANGUAGES,
    *_LANGUAGE_ALIASES.keys(),
)

# Type for language parameter
CodeEditorLanguage = Literal[
    "r",
    "python",
    "julia",
    "sql",
    "javascript",
    "typescript",
    "markup",
    "css",
    "scss",
    "sass",
    "json",
    "markdown",
    "yaml",
    "xml",
    "toml",
    "ini",
    "bash",
    "docker",
    "latex",
    "cpp",
    "rust",
    "diff",
    # Aliases
    "md",
    "html",
    "plain",
    "plaintext",
    "text",
    "txt",
]

# Indentation type
CodeEditorIndentation = Literal["space", "tab"]

# Version of prism-code-editor vendored from bslib
_VERSION_PRISM_CODE_EDITOR = "4.2.0"


def _resolve_language(language: str) -> str:
    """Resolve language aliases to their actual grammar names."""
    if language not in _SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Invalid language: {language!r}. "
            f"Supported languages are: {', '.join(_SUPPORTED_LANGUAGES)}"
        )
    return _LANGUAGE_ALIASES.get(language, language)


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


def code_editor_themes() -> tuple[str, ...]:
    """
    List available code editor themes.

    Returns a tuple of available theme names that can be used with
    :func:`~shiny.ui.input_code_editor`.

    Returns
    -------
    :
        A tuple of available theme names.

    See Also
    --------
    * :func:`~shiny.ui.input_code_editor`
    """
    # These themes are bundled with prism-code-editor
    return (
        "atom-one-dark",
        "dracula",
        "github-dark",
        "github-dark-dimmed",
        "github-light",
        "night-owl",
        "night-owl-light",
        "prism",
        "prism-okaidia",
        "prism-solarized-light",
        "prism-tomorrow",
        "prism-twilight",
        "vs-code-dark",
        "vs-code-light",
    )


def _validate_theme(theme: str, param_name: str) -> str:
    """Validate that a theme name is available."""
    available_themes = code_editor_themes()
    if theme not in available_themes:
        raise ValueError(
            f"Invalid {param_name}: {theme!r}. "
            f"Available themes are: {', '.join(available_themes)}"
        )
    return theme


def _code_editor_dependency_prism() -> HTMLDependency:
    """HTML dependency for prism-code-editor library."""
    return HTMLDependency(
        name="prism-code-editor",
        version=_VERSION_PRISM_CODE_EDITOR,
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


@add_example()
def input_code_editor(
    id: str,
    value: str | Sequence[str] = "",
    label: TagChild = None,
    *,
    language: CodeEditorLanguage = "plain",
    height: str = "auto",
    width: str = "100%",
    theme_light: str = "github-light",
    theme_dark: str = "github-dark",
    read_only: bool = False,
    line_numbers: Optional[bool] = None,
    word_wrap: Optional[bool] = None,
    tab_size: int = 2,
    indentation: CodeEditorIndentation = "space",
    fill: bool = True,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a code editor input.

    Creates an interactive lightweight code editor input with syntax highlighting,
    line numbers, and other basic code editing features powered by Prism Code Editor.

    The editor value is not sent to the server on every keystroke. Instead, updates
    are reflected on the server when the user moves away from the editor (blur) or
    when they press ``Ctrl/Cmd + Enter``.

    Parameters
    ----------
    id
        An input ID.
    value
        Initial code content. Can be a string or a sequence of strings (lines).
    label
        An optional label for the code editor.
    language
        Programming language for syntax highlighting. Supported languages include
        ``"r"``, ``"python"``, ``"julia"``, ``"sql"``, ``"javascript"``,
        ``"typescript"``, ``"html"``, ``"css"``, ``"scss"``, ``"sass"``, ``"json"``,
        ``"markdown"``, ``"yaml"``, ``"xml"``, ``"toml"``, ``"ini"``, ``"bash"``,
        ``"docker"``, ``"latex"``, ``"cpp"``, ``"rust"``, ``"diff"``, and ``"plain"``.
    height
        CSS height of the editor. Set to a specific value like ``"300px"`` for a
        fixed height, or ``"auto"`` to grow with content.
    width
        CSS width of the editor.
    theme_light
        Theme to use in light mode. Use :func:`~shiny.ui.code_editor_themes` to see
        available themes.
    theme_dark
        Theme to use in dark mode. The editor automatically switches between
        ``theme_light`` and ``theme_dark`` based on the current Bootstrap theme.
    read_only
        Whether the editor should be read-only.
    line_numbers
        Whether to show line numbers. Defaults to ``True``, except for ``"markdown"``
        and ``"plain"`` languages where it defaults to ``False``.
    word_wrap
        Whether to wrap long lines. Defaults to ``True`` when ``line_numbers`` is
        ``False``, otherwise ``False``.
    tab_size
        Number of spaces per tab.
    indentation
        Type of indentation: ``"space"`` or ``"tab"``.
    fill
        Whether the code editor should fill its container. When ``True`` (the
        default), the editor participates in the fillable layout system.
    **kwargs
        Additional HTML attributes for the outer container element.

    Returns
    -------
    :
        A code editor input that can be added to a UI definition.

    Notes
    -----
    ::: {.callout-note title="Server value"}
    A string containing the current editor content.

    Unlike text inputs that update on every keystroke, the code editor only sends
    its value to the server when the user presses ``Ctrl/Cmd + Enter`` or when
    the editor loses focus (blur event).
    :::

    Keyboard Shortcuts
    ------------------
    The editor supports the following keyboard shortcuts:

    * ``Ctrl/Cmd + Enter``: Submit the current code to the server
    * ``Ctrl/Cmd + Z``: Undo
    * ``Ctrl/Cmd + Shift + Z``: Redo
    * ``Tab``: Indent selection
    * ``Shift + Tab``: Dedent selection

    Themes
    ------
    The editor automatically switches between ``theme_light`` and ``theme_dark``
    when used with :func:`~shiny.ui.input_dark_mode`. Use
    :func:`~shiny.ui.code_editor_themes` to see all available themes.

    See Also
    --------
    * :func:`~shiny.ui.update_code_editor`
    * :func:`~shiny.ui.code_editor_themes`
    * :func:`~shiny.ui.input_text_area`
    """
    resolved_id = resolve_id(id)

    # Handle value as sequence of lines
    if isinstance(value, (list, tuple)):
        value = "\n".join(str(v) for v in value)
    if not isinstance(value, str):
        raise TypeError("`value` must be a string or sequence of strings")

    # Restore input for bookmarking support
    value = restore_input(resolved_id, default=value)
    if not isinstance(value, str):
        value = str(value) if value is not None else ""

    # Validate inputs
    _check_value_line_count(value)
    language = _resolve_language(language)
    _validate_theme(theme_light, "theme_light")
    _validate_theme(theme_dark, "theme_dark")

    if tab_size < 1:
        raise ValueError("`tab_size` must be a positive integer")

    # Default line_numbers based on language
    if line_numbers is None:
        line_numbers = language not in ("markdown", "plain")

    # Default word_wrap based on line_numbers
    if word_wrap is None:
        word_wrap = not line_numbers

    insert_spaces = indentation == "space"

    # Create the label element
    label_tag = shiny_input_label(resolved_id, label)

    # Create inner container that will hold the actual editor
    editor_inner = tags.div(
        class_="code-editor",
        style=css(display="grid"),
    )

    # Build the custom element
    tag = Tag(
        "bslib-code-editor",
        {
            "id": resolved_id,
            "class": "bslib-mb-spacing",
            "style": css(height=height, width=width),
            "language": language,
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
        label_tag,
        editor_inner,
        *_code_editor_dependencies(),
    )

    # Add fillable classes
    if fill:
        tag.add_class("html-fill-container")
        tag.add_class("html-fill-item")
        editor_inner.add_class("html-fill-item")
    else:
        tag.add_class("html-fill-container")
        editor_inner.add_class("html-fill-item")

    return tag


@add_example()
def update_code_editor(
    id: str,
    *,
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
        Type of indentation: ``"space"`` or ``"tab"``.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    See Also
    --------
    * :func:`~shiny.ui.input_code_editor`
    * :func:`~shiny.ui.code_editor_themes`
    """
    session = require_active_session(session)

    # Validate and process value
    if value is not None:
        if isinstance(value, (list, tuple)):
            value = "\n".join(str(v) for v in value)
        if not isinstance(value, str):
            raise TypeError("`value` must be a string or sequence of strings")
        _check_value_line_count(value)

    # Validate other inputs if provided
    if language is not None:
        language = _resolve_language(language)  # type: ignore[assignment]
    if theme_light is not None:
        _validate_theme(theme_light, "theme_light")
    if theme_dark is not None:
        _validate_theme(theme_dark, "theme_dark")
    if tab_size is not None and tab_size < 1:
        raise ValueError("`tab_size` must be a positive integer")

    # Build message with snake_case keys (matches TypeScript receiveMessage)
    msg = {
        "value": value,
        "language": language,
        "theme_light": theme_light,
        "theme_dark": theme_dark,
        "read_only": read_only,
        "line_numbers": line_numbers,
        "word_wrap": word_wrap,
        "tab_size": tab_size,
        "indentation": indentation,
    }

    session.send_input_message(id, drop_none(msg))
