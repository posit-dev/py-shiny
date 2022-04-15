__all__ = ("include_javascript", "include_css", "include_html", "include_font_face")

import os
import shutil
import tempfile
from typing import Dict, Tuple

from htmltools import tags, Tag, TagAttrArg, HTMLDependency, HTMLDependencySource
from htmltools._util import hash_deterministic


def include_javascript(
    path: str,
    *,
    include_files: bool = True,
    inline: bool = False,
    attrs: Dict[str, TagAttrArg] = {}
) -> HTMLDependency:
    """
    Include a JavaScript file as a :func:`~ui.tags.script` tag.

    Parameters
    ----------
    path
        A path to a JS file.
    include_files
        If ``True``, the JS file may reference other files in the same directory (e.g.,
        use ``fetch()`` to fetch another file).
    inline
        Whether to link to the file path or inline its contents.
    attrs
        Additional attributes to add to the  :func:`~ui.tags.script` tag.

    Note
    ----
    This produces a :func:`~ui.tags.script` tag in the :func:`~ui.tags.head` of the
    document, which means it executes before any of the document's :func:`~ui.tags.body`
    has been parsed, and so DOM manipulation code may need to be wrapped in
    ``document.addEventListener("DOMContentLoaded", () => {});`` (or similar).
    Alternatively, to get :func:`~ui.tags.script` tag included in the
    :func:`~ui.tags.body`, you can do something like this:

    .. code-block:: python

    with open("custom.html", "r", encoding="utf-8") as f:
        custom_js = ui.tags.script(f.read(), type="text/javascript")

    app_ui = ui.page_fluid(..., custom_js, ...)

    See Also
    --------
    ~ui.tags.script
    ~include_css
    ~include_html
    """

    newpath, hash, contents = read_and_copy(path, include_files)

    name = "include-script-" + hash
    source = HTMLDependencySource(subdir=os.path.dirname(newpath))

    if inline:
        return HTMLDependency(
            name,
            DEFAULT_VERSION,
            source=source,
            all_files=include_files,
            head=tags.script(contents, type="text/javascript", **attrs),
        )
    else:
        return HTMLDependency(
            name,
            DEFAULT_VERSION,
            source=source,
            all_files=include_files,
            script=dict(src=os.path.basename(path), **attrs),
        )


def include_css(
    path: str,
    *,
    include_files: bool = True,
    inline: bool = False,
    attrs: Dict[str, TagAttrArg] = {}
) -> HTMLDependency:
    """
    Include CSS

    Parameters
    ----------
    path
        A path to a CSS file.
    include_files
        If ``True``, the CSS file may reference other files in the same directory
        (e.g., use ``@import()`` to import another file).
    inline
        If ``True``, the contents are inlined into a :func:`~ui.tags.style` tag;
        otherwise, a :func:`~ui.tags.link` tag is generated.
    attrs
        Additional attributes to add to the :func:`~ui.tags.style` (or
        :func:`~ui.tags.link`) tag.

    Note
    ----
    This produces a :func:`~ui.tags.style` tag in the :func:`~ui.tags.head` of the
    document, which is advantageous for performance.

    See Also
    --------
    ~ui.tags.style
    ~ui.tags.link
    ~include_javascript
    ~include_html
    """

    newpath, hash, css = read_and_copy(path, include_files)

    name = "include-script-" + hash
    source = HTMLDependencySource(subdir=os.path.dirname(newpath))

    if inline:
        return HTMLDependency(
            name,
            DEFAULT_VERSION,
            source=source,
            all_files=include_files,
            head=tags.style(css, type="text/css", **attrs),
        )
    else:
        return HTMLDependency(
            name,
            DEFAULT_VERSION,
            source=source,
            all_files=include_files,
            stylesheet=dict(href=os.path.basename(path), **attrs),
        )


def include_html(
    path: str, *, include_files: bool = True, attrs: Dict[str, TagAttrArg] = {}
) -> Tag:
    """
    Include an HTML file as an :func:`~ui.tags.iframe`

    Parameters
    ----------
    path
        A path to an HTML file.
    include_files
        Whether to make other files in the ``path``'s directory available.
    attrs
        Additional attributes to add to the :func:`~ui.tags.iframe` tag.

    Returns
    -------
    An :func:`~ui.tags.iframe` tag.

    Note
    ----
    For safety reasons, this function includes the HTML file as a
    :func:`~ui.tags.iframe`, which means it's 'isolated' from the rest of the parent
    document. If instead, you don't want to isolate (meaning, among other things,
    you want the HTML inherit CSS styles from the parent document), you can do
    something like this:

    .. code-block:: python
        from shiny import ui

        with open("custom.html", "r", encoding="utf-8") as f:
            custom_html = ui.HTML(f.read())

        app_ui = ui.page_fluid(..., custom_html, ...)

    See also
    --------
    ~ui.tags.iframe
    ~ui.HTML
    ~include_javascript
    ~include_css
    """

    newpath, hash, _ = read_and_copy(path, include_files)

    return tags.iframe(
        dict(src=os.path.basename(newpath), class_="shiny-iframe", **attrs),
        HTMLDependency(
            "include-iframe-" + hash,
            DEFAULT_VERSION,
            source=HTMLDependencySource(subdir=os.path.dirname(newpath)),
        ),
    )


def include_font_face(path: str):
    pass


def read_and_copy(path: str, include_files: bool) -> Tuple[str, str, str]:
    contents = read_utf8(path)

    tmpdir = tempfile.mkdtemp()
    if include_files:
        # Copy all the directory contents except for path, which we copy later
        # TODO: verify this actually works
        shutil.copytree(
            os.path.dirname(path), tmpdir, ignore=shutil.ignore_patterns(path)
        )

    hash = hash_deterministic(contents)
    basename = os.path.splitext(os.path.basename(path))
    newpath = os.path.join(tmpdir, basename[0] + "-" + hash + basename[1])

    shutil.copy(path, newpath)

    return newpath, hash, contents


def read_utf8(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


DEFAULT_VERSION = "0.0"
