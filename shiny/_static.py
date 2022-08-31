import os
import re
import shutil
from pathlib import Path
from typing import List, Optional, Union


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


def get_default_shinylive_dir() -> str:
    import appdirs

    return os.path.join(appdirs.user_cache_dir("shiny"), "shinylive")


def _installed_shinylive_versions(shinylive_dir: Optional[Path] = None) -> List[str]:
    if shinylive_dir is None:
        shinylive_dir = Path(get_default_shinylive_dir())

    shinylive_dir = Path(shinylive_dir)
    if not shinylive_dir.exists():
        return []
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
