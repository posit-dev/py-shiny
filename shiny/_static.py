import importlib.util
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Optional, Union

if sys.version_info >= (3, 8):
    from typing import Literal, TypedDict
else:
    from typing_extensions import Literal, TypedDict

_SHINYLIVE_DOWNLOAD_URL = "https://pyshiny.netlify.app/shinylive"
_SHINYLIVE_DEFAULT_VERSION = "0.0.2dev"

# This is the same as the FileContentJson type in TypeScript.
class FileContentJson(TypedDict):
    name: str
    content: str
    type: Literal["text", "binary"]


def deploy_static(
    appdir: Union[str, Path],
    destdir: Union[str, Path],
    *,
    subdir: Union[str, Path, None] = None,
    version: str = _SHINYLIVE_DEFAULT_VERSION,
    verbose: bool = False,
    full_shinylive: bool = False,
) -> None:
    """
    Create a statically deployable distribution with a Shiny app.
    """

    shinylive_bundle_dir = _ensure_shinylive_local(version=version)

    # Dynamically import shinylive moodule.
    spec = importlib.util.spec_from_file_location(
        "shinylive", str(shinylive_bundle_dir / "scripts" / "shinylive.py")
    )
    if spec is None:
        raise RuntimeError(
            "Could not import scripts/shinylive.py from shinylive bundle."
        )
    shinylive = importlib.util.module_from_spec(spec)
    sys.modules["shinylive"] = shinylive
    spec.loader.exec_module(shinylive)  # type: ignore

    # Call out to shinylive module to do deployment.
    shinylive.deploy(
        appdir,
        destdir,
        subdir=subdir,
        verbose=verbose,
        full_shinylive=full_shinylive,
    )


def remove_shinylive_local(
    shinylive_dir: Union[str, Path, None] = None,
    version: Optional[str] = None,
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

    if target_dir.exists():
        shutil.rmtree(target_dir)
    else:
        print(f"{target_dir} does not exist.")


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
        destdir.mkdir(parents=True)

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
    import urllib.request

    if destdir is None:
        destdir = get_default_shinylive_dir()

    destdir = Path(destdir)
    tmp_name = None

    try:
        bundle_url = f"{url}/shinylive-{version}.tar.gz"
        print(f"Downloading {bundle_url}...")
        tmp_name, _ = urllib.request.urlretrieve(bundle_url)

        print(f"Unzipping to {destdir}")
        with tarfile.open(tmp_name) as tar:
            tar.extractall(destdir)
    finally:
        if tmp_name is not None:
            # Can simplify this block after we drop Python 3.7 support.
            if sys.version_info >= (3, 8):
                Path(tmp_name).unlink(missing_ok=True)
            else:
                if os.path.exists(tmp_name):
                    os.remove(tmp_name)


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
