import base64
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Callable, List, Optional, Union


if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

_SHINYLIVE_DOWNLOAD_URL = "https://pyshiny.netlify.app/shinylive"
_SHINYLIVE_DEFAULT_VERSION = "0.0.1dev"

# This is the same as the FileContentJson type in TypeScript.
class FileContentJson(TypedDict):
    name: str
    content: str
    type: Literal["text", "binary"]


def deploy_static(
    appdir: Union[str, Path],
    destdir: Union[str, Path],
    *,
    overwrite: bool = False,
    subdir: Union[str, Path, None] = None,
    version: str = _SHINYLIVE_DEFAULT_VERSION,
    verbose: bool = False,
) -> None:
    """
    Create a statically deployable distribution with a Shiny app.
    """

    def verbose_print(*args: object) -> None:
        if verbose:
            print(*args)

    appdir = Path(appdir)
    destdir = Path(destdir)

    if not (appdir / "app.py").exists():
        raise ValueError(f"Directory {appdir} must contain a file named app.py.")

    if subdir is None:
        subdir = ""
    subdir = Path(subdir)
    if subdir.is_absolute():
        raise ValueError("subdir must be a relative path")

    shinylive_bundle_dir = _ensure_shinylive_local(version=version)

    print(f"Copying {shinylive_bundle_dir}/ to {destdir}/")
    if not destdir.exists():
        destdir.mkdir()

    # destdir_rel: Union[str, None] = None
    # if _is_relative_to(destdir, appdir):
    #     destdir_rel = str(Path(destdir).relative_to(Path(appdir)))

    # After we drop Python 3.7 support, this can be replaced with the shutil.copytree
    # call below.
    _copy_recursive(
        shinylive_bundle_dir,
        destdir,
        copy_function=_copy_fn(overwrite, verbose_print=verbose_print),
    )
    # shutil.copytree(
    #     shinylive_bundle_dir,
    #     destdir,
    #     copy_function=_copy_fn(overwrite, verbose_print=verbose_print),
    #     dirs_exist_ok=True,
    # )

    app_files: List[FileContentJson] = []
    # Recursively iterate over files in app directory, and collect the files into
    # app_files data structure.
    exclude_names = {"__pycache__", "venv", ".venv"}
    for root, dirs, files in os.walk(appdir, topdown=True):
        root = Path(root)

        if _is_relative_to(Path(root), destdir):
            # In case destdir is inside of the appdir, don't copy those files.
            continue

        dirs[:] = [d for d in dirs if not d.startswith(".")]
        dirs[:] = set(dirs) - exclude_names
        rel_dir = root.relative_to(appdir)
        files = [f for f in files if not f.startswith(".")]
        files = [f for f in files if f not in exclude_names]
        files.sort()

        # Move app.py to first in list.
        if "app.py" in files:
            app_py_idx = files.index("app.py")
            files.insert(0, files.pop(app_py_idx))

        # Add the file to the app_files list.
        for filename in files:
            if rel_dir == ".":
                output_filename = filename
            else:
                output_filename = str(rel_dir / filename)

            if filename == "shinylive.js":
                print(
                    f"Warning: Found shinylive.js in source directory '{appdir}/{rel_dir}'. Are you including a shinylive distribution in your app?"
                )

            type: Literal["text", "binary"] = "text"
            try:
                with open(root / filename, "r") as f:
                    file_content = f.read()
                    type = "text"
            except UnicodeDecodeError:
                # If text failed, try binary.
                with open(root / filename, "rb") as f:
                    file_content_bin = f.read()
                    file_content = base64.b64encode(file_content_bin).decode("utf-8")
                    type = "binary"

            app_files.append(
                {
                    "name": output_filename,
                    "content": file_content,
                    "type": type,
                }
            )

    # Write the index.html, editor/index.html, and app.json in the destdir.
    html_source_dir = shinylive_bundle_dir / "shinylive/shiny_static"
    app_destdir = destdir / subdir

    # For a subdir like a/b/c, this will be ../../../
    subdir_inverse = "/".join([".."] * _path_length(subdir))
    if subdir_inverse != "":
        subdir_inverse += "/"

    if not app_destdir.exists():
        app_destdir.mkdir()

    _copy_file_and_substitute(
        src=html_source_dir / "index.html",
        dest=app_destdir / "index.html",
        search_str="{{REL_PATH}}",
        replace_str=subdir_inverse,
    )

    editor_destdir = app_destdir / "edit"
    if not editor_destdir.exists():
        editor_destdir.mkdir()
    _copy_file_and_substitute(
        src=html_source_dir / "edit" / "index.html",
        dest=(editor_destdir / "index.html"),
        search_str="{{REL_PATH}}",
        replace_str=subdir_inverse,
    )

    app_json_output_file = app_destdir / "app.json"

    print("Writing to " + str(app_json_output_file), end="")
    json.dump(app_files, open(app_json_output_file, "w"))
    print(":", app_json_output_file.stat().st_size, "bytes")

    print(
        f"\nRun the following to serve the app:\n  python3 -m http.server --directory {destdir} 8008"
    )


def _copy_fn(
    overwrite: bool, verbose_print: Callable[..., None] = lambda x: None
) -> Callable[..., None]:
    """Returns a function that can be used as a copy_function for shutil.copytree.

    If overwrite is True, the copy function will overwrite files that already exist.
    If overwrite is False, the copy function will not overwrite files that already exist.
    """

    def mycopy(src: str, dst: str, **kwargs: object) -> None:
        if os.path.exists(dst):
            if overwrite:
                verbose_print(f"Overwriting {dst}")
                os.remove(dst)
            else:
                verbose_print(f"Skipping {dst}")
                return

        shutil.copy2(src, dst, **kwargs)

    return mycopy


def _path_length(path: Union[str, Path]) -> int:
    """Returns the number of elements in a path.

    For example 'a' has length 1, 'a/b' has length 2, etc.
    """

    path = str(path)
    if os.path.isabs(path):
        raise ValueError("path must be a relative path")

    # Unfortunately, there's no equivalent of os.path.normpath for Path objects.
    path = os.path.normpath(path)
    if path == ".":
        return 0

    # On Windows, replace backslashes with forward slashes.
    if os.name == "nt":
        path.replace("\\", "/")

    return len(path.split("/"))


def _copy_file_and_substitute(
    src: Union[str, Path], dest: Union[str, Path], search_str: str, replace_str: str
) -> None:
    with open(src, "r") as fin:
        in_content = fin.read()
        in_content = in_content.replace(search_str, replace_str)
        with open(dest, "w") as fout:
            fout.write(in_content)


def remove_shinylive_local(
    shinylive_dir: Union[str, Path, None] = None,
    version: Optional[str] = _SHINYLIVE_DEFAULT_VERSION,
) -> None:
    """Removes local copy of shinylive.

    Parameters
    ----------
    shinylive_dir
        The directory where shinylive is stored. If None, the default directory will
        be used.

    version
        If a version is specified, only that version will be removed.
        If None, all local versions of shinylive will be removed.
    """

    if shinylive_dir is None:
        shinylive_dir = get_default_shinylive_dir()

    shinylive_dir = Path(shinylive_dir)

    target_dir = shinylive_dir
    if version is not None:
        target_dir = target_dir / f"shinylive-{version}"

    shutil.rmtree(target_dir)


def _ensure_shinylive_local(
    destdir: Union[Path, None] = None,
    version: str = _SHINYLIVE_DEFAULT_VERSION,
    url: str = _SHINYLIVE_DOWNLOAD_URL,
) -> Path:
    """Ensure that there is a local copy of shinylive."""

    if destdir is None:
        destdir = Path(get_default_shinylive_dir())

    if not destdir.exists():
        print("Creating directory " + str(destdir))
        destdir.mkdir()

    shinylive_bundle_dir = destdir / f"shinylive-{version}"
    if not shinylive_bundle_dir.exists():
        print(f"{shinylive_bundle_dir} does not exist.")
        download_shinylive(url=url, version=version, destdir=destdir)

    return shinylive_bundle_dir


def download_shinylive(
    destdir: Union[str, Path, None] = None,
    version: str = _SHINYLIVE_DEFAULT_VERSION,
    url: str = _SHINYLIVE_DOWNLOAD_URL,
) -> None:
    import tarfile
    import tempfile
    import urllib.request

    if destdir is None:
        destdir = get_default_shinylive_dir()

    destdir = Path(destdir)

    with tempfile.NamedTemporaryFile() as tmp:

        bundle_url = f"{url}/shinylive-{version}.tar.gz"
        print(f"Downloading {bundle_url}...")
        urllib.request.urlretrieve(bundle_url, tmp.name)

        print(f"Unzipping to {destdir}")
        with tarfile.open(tmp.name) as tar:
            tar.extractall(destdir)


def get_default_shinylive_dir() -> str:
    import appdirs

    return os.path.join(appdirs.user_cache_dir("shiny"), "shinylive")


def copy_shinylive_local(
    source_dir: Union[str, Path],
    destdir: Optional[Union[str, Path]] = None,
    version: str = _SHINYLIVE_DEFAULT_VERSION,
):
    if destdir is None:
        destdir = Path(get_default_shinylive_dir())

    destdir = Path(destdir)

    target_dir = destdir / ("shinylive-" + version)

    if target_dir.exists():
        shutil.rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)


def _installed_shinylive_versions(shinylive_dir: Optional[Path] = None) -> List[str]:
    if shinylive_dir is None:
        shinylive_dir = Path(get_default_shinylive_dir())

    shinylive_dir = Path(shinylive_dir)
    subdirs = shinylive_dir.iterdir()
    subdirs = [re.sub("^shinylive-", "", str(s)) for s in subdirs]
    return subdirs


def print_shinylive_local_info() -> None:

    print(
        f"""    Local shinylive dir:
        {get_default_shinylive_dir()}

    Installed versions:
        {", ".join(_installed_shinylive_versions())}"""
    )


# A wrapper for shutil.copytree. In Python >= 3.8, we can use dirs_exist_ok=True so that
# it doesn't error if the destination dir or subdirs already exist. In <= 3.7, we need
# to ignore directories manually. After we drop 3.7 support, we can remove this wrapper
# function.
def _copy_recursive(
    source: Path,
    dest: Path,
    copy_function: Callable[..., None] = shutil.copy2,
) -> None:
    if sys.version_info >= (3, 8):
        shutil.copytree(source, dest, copy_function=copy_function, dirs_exist_ok=True)
    else:
        source = Path(source)
        dest = Path(dest)

        if source.is_dir():
            if not dest.is_dir():
                dest.mkdir()
            files = source.iterdir()
            for f in files:
                _copy_recursive(source / f, dest / f)
        else:
            shutil.copyfile(source, dest)


def _is_relative_to(path: Path, base: Path) -> bool:
    """
    Wrapper for `PurePath.is_relative_to`, which was added in Python 3.9.
    """
    if sys.version_info >= (3, 9):
        return path.is_relative_to(base)
    else:
        try:
            path.relative_to(base)
            return True
        except ValueError:
            return False
