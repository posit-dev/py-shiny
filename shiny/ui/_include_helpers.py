from __future__ import annotations

from warnings import warn

__all__ = ("include_js", "include_css", "include_bootstrap_css")

import glob
import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Literal, Optional

# TODO: maybe these include_*() functions should actually live in htmltools?
from htmltools import HTMLDependency, Tag, TagAttrValue, head_content, tags
from packaging.version import Version

from .._docstring import add_example
from .._versions import bootstrap as base_bootstrap_version
from ._html_deps_external import bootstrap_deps_suppress

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
    Include a JavaScript file.

    Parameters
    ----------
    path
        A path to a JS file.
    method
        One of the following:

        * ``"link"`` is the link to the CSS file via a :func:`~shiny.ui.tags.link` tag. This
          method is generally preferable to ``"inline"`` since it allows the browser to
          cache the file.
        * ``"link_files"`` is the same as ``"link"``, but also allow for the CSS file to
          request other files within ``path``'s immediate parent directory (e.g.,
          ``@import()`` another file). Note that this isn't the default behavior because
          you should **be careful not to include files in the same directory as ``path``
          that contain sensitive information**. A good general rule of thumb to follow
          is to have ``path`` be located in a subdirectory of the app directory. For
          example, if the app's source is located at ``/app/app.py``, then ``path``
          should be somewhere like ``/app/css/custom.css`` (and all the other relevant
          accompanying 'safe' files should be located under ``/app/css/``).
        * ``"inline"`` is the inline the CSS file contents within a
          :func:`~shiny.ui.tags.style` tag.
    **kwargs
        Attributes which are passed on to `~shiny.ui.tags.script`.


    Returns
    -------
    :
        A :func:`~shiny.ui.tags.script` tag.

    Note
    ----
    This places a :func:`~shiny.ui.tags.script` tag in the :func:`~shiny.ui.tags.body` of the
    document. If you want to place the tag in the :func:`~shiny.ui.tags.head` of the
    document instead, you can wrap it in ``head_content`` (in this case, just
    make sure you're aware that the DOM probably won't be ready when the script
    is executed).

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
    * :func:`~shiny.ui.tags.script`
    * :func:`~shiny.ui.include_css`
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
    Include a CSS file.

    Parameters
    ----------
    path
        A path to a CSS file.
    method
        One of the following:

        * ``"link"`` is the link to the CSS file via a :func:`~shiny.ui.tags.link` tag. This
          method is generally preferable to ``"inline"`` since it allows the browser to
          cache the file.
        * ``"link_files"`` is the same as ``"link"``, but also allow for the CSS file to
          request other files within ``path``'s immediate parent directory (e.g.,
          ``@import()`` another file). Note that this isn't the default behavior because
          you should **be careful not to include files in the same directory as ``path``
          that contain sensitive information**. A good general rule of thumb to follow
          is to have ``path`` be located in a subdirectory of the app directory. For
          example, if the app's source is located at ``/app/app.py``, then ``path``
          should be somewhere like ``/app/css/custom.css`` (and all the other relevant
          accompanying 'safe' files should be located under ``/app/css/``).
        * ``"inline"`` is the inline the CSS file contents within a
          :func:`~shiny.ui.tags.style` tag.


    Returns
    -------
    :

        If ``method="inline"``, returns a :func:`~shiny.ui.tags.style` tag; otherwise, returns a
        :func:`~shiny.ui.tags.link` tag.

    Note
    ----
    By default this places a :func:`~shiny.ui.tags.link` (or :func:`~shiny.ui.tags.style`) tag in
    the :func:`~shiny.ui.tags.body` of the document, which isn't optimal for performance, and
    may result in a Flash of Unstyled Content (FOUC). To instead place the CSS in the
    :func:`~shiny.ui.tags.head` of the document, you can wrap it in ``head_content``:

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
    * :func:`~shiny.ui.tags.style`
    * :func:`~shiny.ui.tags.link`
    * :func:`~shiny.ui.include_js`
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


@add_example()
def include_bootstrap_css(
    theme: Path | str | HTMLDependency,
    bs_version: Optional[Version | str] = None,
) -> list[HTMLDependency]:
    """
    Replace the built-in Shiny Bootstrap CSS theme.

    Parameters
    ----------
    theme
        The theme to include. It can be a path to a file, or an
        :class:`~htmltools.HTMLDependency`.
    bs_version
        The version of Bootstrap used by this `theme`, used to check for compatibility
        with the version of Bootstrap used by Shiny. If not provided, the version is
        discovered from one of several places:

        * If the :class:`~htmltools.HTMLDependency` includes a `bs_version` attribute,
          that is used.
        * If `theme` is a file, the version is discovered by parsing the Bootstrap
          banner comment in the file, which should look something like
          `* Bootstrap v4.5.2`.
        * If `theme` is an :class:`~htmltools.HTMLDependency`, the first stylesheet in
          the dependency is parsed for the version comment mentioned above.

    Returns
    -------
    :
        A list of HTMLDependencies, the specified `theme` and a special
        :class:`~htmltools.HTMLDependency` to suppress Shiny's built-in Bootstrap CSS.

    Raises
    ------
    RuntimeError
        When the major versions of theme's `bs_version` and Shiny's built-in Bootstrap
        version are different, indicating incompatibility between the theme's Bootstrap
        version and the base version.

    Warns
    -----
    RuntimeWarning
        When the theme's Bootstrap version and Shiny's built-in Bootstrap version are
        not identical but the major versions match, indicating a potential for
        unexpected issues.

    See Also
    --------
    * Use :func:`~shiny.ui.include_css` if your CSS file contains styles that should be
      applied *in addition to* (rather than replacing) Shiny's built-in Bootstrap theme.

    """
    if isinstance(theme, (Path, str)):
        theme_dep = head_content(include_css(theme))
    else:
        theme_dep = theme

    # Check compatibility _after_ resolving the dependency so that
    # `include_css()` has a chance to check that the theme file exists.
    check_bootstrap_compatibility(theme, bs_version)

    return [
        *bootstrap_deps_suppress(["css"]),
        theme_dep,
    ]


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


def check_bootstrap_compatibility(
    theme: Path | str | HTMLDependency,
    bs_version: Optional[Version | str] = None,
) -> None:
    if isinstance(theme, HTMLDependency):
        check_bootstrap_compatibility_dep(theme, bs_version)
        return

    if bs_version is not None:
        check_bootstrap_compatibility_version(bs_version)
        return

    if isinstance(theme, (Path, str)):
        check_bootstrap_compatibility_file(theme)
        return

    raise RuntimeError(
        "Invalid theme argument. Must be a Path, str, or HTMLDependency."
    )


def check_bootstrap_compatibility_dep(
    theme: HTMLDependency,
    bs_version: Optional[Version | str] = None,
) -> None:
    if bs_version is not None:
        check_bootstrap_compatibility_version(
            bs_version=bs_version,
            name=theme.name,
            version=theme.version,
        )

    if hasattr(theme, "bs_version"):
        check_bootstrap_compatibility_version(
            bs_version=theme.__getattribute__("bs_version"),
            name=theme.name,
            version=theme.version,
        )

    source_dir = theme.source_path_map()["source"]

    if not theme.stylesheet:
        return

    sheet = theme.stylesheet[0]["href"]

    check_bootstrap_compatibility_file(Path(source_dir) / Path(sheet).name)


def check_bootstrap_compatibility_file(theme: str | Path):
    theme = Path(theme)

    if theme.suffix != ".css":
        warn(
            "Cannot check Bootstrap compatibility of non-CSS files. "
            + f"Skipping: {theme}",
        )

    version = ""
    with open(theme, "r", encoding="utf-8") as f:
        for line in f:
            if re.search(r"\* Bootstrap\s+v", line):
                match = re.search(r"v(\d+\.\d+(\.\d+)?)", line)
                if match:
                    version = match.group(1)
                    break

    if version:
        check_bootstrap_compatibility_version(version)


def check_bootstrap_compatibility_version(
    bs_version: Version | str,
    name: Optional[str] = None,
    version: Optional[Version] = None,
) -> None:
    base_version = Version(base_bootstrap_version)

    if isinstance(bs_version, str):
        bs_version = Version(bs_version)

    if bs_version == base_version:
        return

    the_theme = f"'{name}'" if name else ""
    the_theme += f" ({version})" if version else ""
    the_theme = f"theme {the_theme}" if the_theme else "`theme`"

    if bs_version.major != base_version.major:
        raise RuntimeError(
            "Bootstrap version mismatch:"
            + f"\n  * {bs_version} from {the_theme}."
            + f"\n  * {base_version} from Shiny."
            + "\n  ! These versions of Bootstrap are incompatible."
        )

    warn(
        "Bootstrap version mismatch:"
        + f"\n  * {bs_version} from {the_theme}."
        + f"\n  * {base_version} from Shiny."
        + "\n  ! This version mismatch may cause unexpected issues.",
        RuntimeWarning,
    )


DEFAULT_VERSION = "0.0"
