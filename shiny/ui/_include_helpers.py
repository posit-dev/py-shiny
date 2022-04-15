__all__ = ("include_javascript", "include_css", "include_html")

import glob
import os
import shutil
import tempfile
from typing import Dict, Literal, Tuple

# TODO: maybe these include_*() functions should actually live in htmltools?
from htmltools import tags, Tag, TagAttrArg, HTMLDependency
from htmltools._util import hash_deterministic

from .._docstring import add_example

# TODO: it's bummer that, when method="link_files" and path is in the same directory
# as the app, the app's source will be included. Should we just not copy .py/.r files?


@add_example()
def include_javascript(
    path: str, *, method: Literal["link", "link_files", "inline"] = "link"
) -> Tag:
    """
    Include a JavaScript file

    Parameters
    ----------
    path
        A path to a JS file.
    method
        One of the following:
          * ``"link"``: Link to the JS file via a :func:`~ui.tags.script` tag. This
            method is generally preferrable to ``"inline"`` since it allows the browser
            to cache the file.
          * ``"link_files"``: Same as ``"link"``, but also allow for the CSS file to
            request other files within ``path``'s immediate parent directory (e.g.,
            ``fetch()`` the contents of another file). Note that this isn't the default
            behavior because you should **be careful not to include files in the same
            directory as ``path`` that contain sensitive information**. A good general
            rule of thumb to follow is to have ``path`` be located in a subdirectory of
            the app directory. For example, if the app's source is located at
            ``/app/app.py``, then ``path`` should be somewhere like
            ``/app/js/custom.js`` (and all the other relevant accompanying 'safe' files
            should be located under ``/app/js/``).
          * ``"inline"``: Inline the JS file contents within a :func:`~ui.tags.script`
            tag.


    Returns
    -------
    A :func:`~ui.tags.script` tag.

    Note
    ----
    This places a :func:`~ui.tags.script` tag in the :func:`~ui.tags.body` of the
    document. If instead, you want to place the tag in the :func:`~ui.tags.head` of the
    document, you can wrap it in ``head_content`` (in this case, just make sure you're
    aware that the DOM probably won't be ready when the script is executed).

    .. code-block:: python

    from htmltools import head_content from shiny import ui

    ui.fluidPage(
        head_content(ui.include_javascript("custom.js"))
    )

    See Also
    --------
    ~ui.tags.script
    ~include_css
    ~include_html
    """

    if method == "inline":
        return tags.script(read_utf8(path), type="text/javascript")

    include_files = method == "link_files"
    path_dest, hash = maybe_copy_files(path, include_files)

    dep, src = create_include_dependency("include-js-" + hash, path_dest, include_files)

    return tags.script(dep, src=src)


@add_example()
def include_css(
    path: str, *, method: Literal["link", "link_files", "inline"] = "link"
) -> Tag:
    """
    Include a CSS file

    Parameters
    ----------
    path
        A path to a CSS file.
    method
        One of the following:
          * ``"link"``: Link to the CSS file via a :func:`~ui.tags.link` tag. This
            method is generally preferrable to ``"inline"`` since it allows the browser
            to cache the file.
          * ``"link_files"``: Same as ``"link"``, but also allow for the CSS file to
            request other files within ``path``'s immediate parent directory (e.g.,
            ``@import()`` another file). Note that this isn't the default behavior
            because you should **be careful not to include files in the same directory
            as ``path`` that contain sensitive information**. A good general rule of
            thumb to follow is to have ``path`` be located in a subdirectory of the app
            directory. For example, if the app's source is located at ``/app/app.py``,
            then ``path`` should be somewhere like ``/app/css/custom.css`` (and all the
            other relevant accompanying 'safe' files should be located under
            ``/app/css/``).
          * ``"inline"``: Inline the CSS file contents within a :func:`~ui.tags.style`
            tag.

    Returns
    -------
    If ``method="inline"``, returns a :func:`~ui.tags.style` tag; otherwise, returns a
    :func:`~ui.tags.link` tag.

    Note
    ----
    By default this places a :func:`~ui.tags.link` (or :func:`~ui.tags.style`) tag in
    the :func:`~ui.tags.body` of the document, which isn't optimal for performance, and
    may result in a Flash of Unstyled Content (FOUC). To instead place the CSS in the
    :func:`~ui.tags.head` of the document, you can wrap it in ``head_content``:

    .. code-block:: python

    from htmltools import head_content from shiny import ui

    ui.fluidPage(
        head_content(ui.include_css("custom.css"))
    )

    See Also
    --------
    ~ui.tags.style
    ~ui.tags.link
    ~include_javascript
    ~include_html
    """

    if method == "inline":
        return tags.style(read_utf8(path), type="text/css")

    include_files = method == "link_files"
    path_dest, hash = maybe_copy_files(path, include_files)

    dep, src = create_include_dependency(
        "include-css-" + hash, path_dest, include_files
    )

    return tags.link(dep, href=src, rel="stylesheet")


# TODO: maybe support remote URLs?
@add_example()
def include_html(
    path: str,
    *,
    method: Literal["link", "link_files"] = "link",
    attrs: Dict[str, TagAttrArg] = {},
) -> Tag:
    """
    Include an HTML file

    Parameters
    ----------
    path
        A path to an HTML file.
    method
        One of the following:
          * ``"link"``: Link to the CSS file via a :func:`~ui.tags.link` tag.
          * ``"link_files"``: Same as ``"link"``, but also allow for the HTML file to
            request other files within ``path``'s immediate parent directory (e.g.,
            include an HTML ``<img>`` that points to another local file). This isn't the
            default behavior because you should **be careful not to include files in the
            same directory as ``path`` that contain sensitive information**. A good
            general rule of thumb to follow is to have ``path`` be located in a
            subdirectory of the app directory. For example, if the app's source is
            located at ``/app/app.py``, then ``path`` should be somewhere like
            ``/app/html/index.html`` (and all the other relevant accompanying 'safe'
            files should be located under ``/app/html/``).
    attrs
        Additional attributes to add to the :func:`~ui.tags.iframe` tag.

    Returns
    -------
    A :func:`~ui.tags.iframe` tag.

    Note
    ----
    For safety reasons, this function includes the HTML file as a
    :func:`~ui.tags.iframe`, which means it's 'isolated' from the rest of the parent
    document. If instead, you don't want to isolate (meaning, among other things, you
    want the HTML inherit CSS styles from the parent document), you can do something
    like this:

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

    include_files = method == "link_files"
    path_dest, hash = maybe_copy_files(path, include_files)

    dep, src = create_include_dependency(
        "include-html-" + hash, path_dest, include_files
    )

    default_attrs: Dict[str, TagAttrArg] = {
        "src": src,
        "scrolling": "no",
        "seamless": "seamless",
        "frameBorder": "0",
    }

    return tags.iframe(default_attrs, dep, **attrs)


# ---------------------------------------------------------------------------
# Include helpers
# ---------------------------------------------------------------------------


def create_include_dependency(
    name: str, path: str, include_files: bool
) -> Tuple[HTMLDependency, str]:

    dep = HTMLDependency(
        name,
        DEFAULT_VERSION,
        source={"subdir": os.path.dirname(path)},
        all_files=include_files,
    )

    # source_path_map() tells us where the source subdir is mapped to on the client
    # (i.e., session._register_web_dependency() uses the same thing to determine where
    # to mount the subdir, but we can't assume an active session at this point).
    src = os.path.join(dep.source_path_map()["href"], os.path.basename(path))

    return dep, src


def maybe_copy_files(path: str, include_files: bool) -> Tuple[str, str]:
    hash = get_hash(path, include_files)

    # To avoid unnecessary work when the same file is included multiple times,
    # use a directory scoped by a hash of the file.
    tmpdir = os.path.join(tempfile.gettempdir(), "shiny_include_files", hash)
    path_dest = os.path.join(tmpdir, os.path.basename(path))

    # Since the hash/tmpdir should represent all the files in the path's directory,
    # we can simply return here
    if os.path.exists(path_dest):
        return path_dest, hash

    # Otherwise, make sure we have a clean slate
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)

    if include_files:
        shutil.copytree(os.path.dirname(path), tmpdir)
    else:
        os.makedirs(tmpdir, exist_ok=True)
        shutil.copy(path, path_dest)

    return path_dest, hash


def get_hash(path: str, include_files: bool) -> str:
    if include_files:
        key = get_file_key(path)
    else:
        dir = os.path.dirname(path)
        files = glob.iglob(os.path.join(dir, "**"), recursive=True)
        key = "\n".join([get_file_key(x) for x in files])
    return hash_deterministic(key)


def get_file_key(path: str) -> str:
    return path + "-" + str(os.path.getmtime(path))


def read_utf8(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


DEFAULT_VERSION = "0.0"
