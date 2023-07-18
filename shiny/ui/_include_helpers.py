from __future__ import annotations

__all__ = ("include_js", "include_css")

import glob
import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Literal

# TODO: maybe these include_*() functions should actually live in htmltools?
from htmltools import HTMLDependency, Tag, TagAttrValue, tags

from .._docstring import add_example

# TODO: it's bummer that, when method="link_files" and path is in the same directory
# as the app, the app's source will be included. Should we just not copy .py/.r files?


@add_example()
def include_js(
    path: Path | str,
    *,
    method: Literal["link", "link_files", "inline"] = "link",
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Include a JavaScript file

    Parameters
    ----------
    path
        A path to a JS file.
    method
        One of the following: ``"link"``, ``"link_files"``, or ``"inline"``. ``"link"``
        is the link to the CSS file via a :func:`~ui.tags.link` tag. This method is
        generally preferrable to ``"inline"`` since it allows the browser to cache the
        file. ``"link_files"`` is the same as ``"link"``, but also allow for the CSS
        file to request other files within ``path``'s immediate parent directory (e.g.,
        ``@import()`` another file). Note that this isn't the default behavior because
        you should **be careful not to include files in the same directory as ``path``
        that contain sensitive information**. A good general rule of thumb to follow is
        to have ``path`` be located in a subdirectory of the app directory. For example,
        if the app's source is located at ``/app/app.py``, then ``path`` should be
        somewhere like ``/app/css/custom.css`` (and all the other relevant accompanying
        'safe' files should be located under ``/app/css/``). And finally, ``"inline"``
        is the inline the CSS file contents within a :func:`~ui.tags.style` tag.
    **kwargs
        Attributes which are passed on to `~ui.tags.script`


    Returns
    -------
    :
        A :func:`~ui.tags.script` tag.

    Note
    ----
    This places a :func:`~ui.tags.script` tag in the :func:`~ui.tags.body` of the
    document. If instead, you want to place the tag in the :func:`~ui.tags.head` of the
    document, you can wrap it in ``head_content`` (in this case, just make sure you're
    aware that the DOM probably won't be ready when the script is executed).

    ```{python}
    #| eval: false
    ui.page_fluid(
        ui.head_content(ui.include_js("custom.js")),
    )

    # Alternately you can inline Javscript by changing the method.
    ui.page_fluid(
        ui.head_content(ui.include_js("custom.js", method = "inline")),
    )
    ```

    See Also
    --------
    ~ui.tags.script
    ~include_css
    """
    file_path = check_path(path)

    if method == "inline":
        return tags.script(read_utf8(file_path), **kwargs)

    include_files = method == "link_files"
    path_dest, hash = maybe_copy_files(file_path, include_files)

    dep, src = create_include_dependency("include-js-" + hash, path_dest, include_files)

    return tags.script(dep, src=src, **kwargs)


@add_example()
def include_css(
    path: Path | str, *, method: Literal["link", "link_files", "inline"] = "link"
) -> Tag:
    """
    Include a CSS file

    Parameters
    ----------
    path
        A path to a CSS file.
    method
        One of the following: ``"link"``, ``"link_files"``, or ``"inline"``. ``"link"``
        is the link to the CSS file via a :func:`~ui.tags.link` tag. This method is
        generally preferrable to ``"inline"`` since it allows the browser to cache the
        file. ``"link_files"`` is the same as ``"link"``, but also allow for the CSS
        file to request other files within ``path``'s immediate parent directory (e.g.,
        ``@import()`` another file). Note that this isn't the default behavior because
        you should **be careful not to include files in the same directory as ``path``
        that contain sensitive information**. A good general rule of thumb to follow is
        to have ``path`` be located in a subdirectory of the app directory. For example,
        if the app's source is located at ``/app/app.py``, then ``path`` should be
        somewhere like ``/app/css/custom.css`` (and all the other relevant accompanying
        'safe' files should be located under ``/app/css/``). And finally, ``"inline"``
        is the inline the CSS file contents within a :func:`~ui.tags.style` tag.


    Returns
    -------
    :

        If ``method="inline"``, returns a :func:`~ui.tags.style` tag; otherwise, returns a
        :func:`~ui.tags.link` tag.

    Note
    ----
    By default this places a :func:`~ui.tags.link` (or :func:`~ui.tags.style`) tag in
    the :func:`~ui.tags.body` of the document, which isn't optimal for performance, and
    may result in a Flash of Unstyled Content (FOUC). To instead place the CSS in the
    :func:`~ui.tags.head` of the document, you can wrap it in ``head_content``:

    ```{python}
    #| eval: false
    from htmltools import head_content
    from shiny import ui

    ui.page_fluid(
        ui.head_content(ui.include_css("custom.css")),

        # You can also inline css by passing a dictionary with a `style` element.
        ui.div(
            {"style": "font-weight: bold;"},
            ui.p("Some text!"),
        )
    )
    ```

    See Also
    --------
    ~ui.tags.style
    ~ui.tags.link
    ~include_js
    """

    file_path = check_path(path)
    if method == "inline":
        return tags.style(read_utf8(file_path), type="text/css")

    include_files = method == "link_files"
    path_dest, hash = maybe_copy_files(file_path, include_files)

    dep, src = create_include_dependency(
        "include-css-" + hash, path_dest, include_files
    )

    return tags.link(dep, href=src, rel="stylesheet")


# ---------------------------------------------------------------------------
# Include helpers
# ---------------------------------------------------------------------------


def check_path(path: Path | str) -> Path:
    path = Path(path)
    if not path.exists():
        err = f"""
        {path.absolute()} does not exist.
        Files are typically placed in the app directory and refered to with 'Path(__file__) / {path.name}'
        """
        raise RuntimeError(err)
    return path


def create_include_dependency(
    name: str, path: str, include_files: bool
) -> tuple[HTMLDependency, str]:
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


def maybe_copy_files(path: Path | str, include_files: bool) -> tuple[str, str]:
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


def get_hash(path: Path | str, include_files: bool) -> str:
    if include_files:
        key = get_file_key(path)
    else:
        dir = os.path.dirname(path)
        files = glob.iglob(os.path.join(dir, "**"), recursive=True)
        key = "\n".join([get_file_key(x) for x in files])
    return hash_deterministic(key)


def get_file_key(path: Path | str) -> str:
    path = Path(path)
    return str(path) + "-" + str(path.stat().st_mtime)


def hash_deterministic(s: str) -> str:
    """
    Returns a deterministic hash of the given string.
    """
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def read_utf8(path: Path | str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


DEFAULT_VERSION = "0.0"
