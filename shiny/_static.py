from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Optional


def remove_shinylive_local(
    shinylive_dir: Optional[Path] = None,
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

    target_dir = shinylive_dir
    if version is not None:
        target_dir = target_dir / f"shinylive-{version}"

    if target_dir.exists():
        shutil.rmtree(target_dir)


def get_default_shinylive_dir() -> Path:
    import appdirs  # pyright: ignore[reportMissingTypeStubs]

    return Path(appdirs.user_cache_dir("shiny")) / "shinylive"  # pyright: ignore


def _installed_shinylive_versions(shinylive_dir: Optional[Path] = None) -> list[str]:
    if shinylive_dir is None:
        shinylive_dir = get_default_shinylive_dir()

    if not shinylive_dir.exists():
        return []
    subdirs = next(os.walk(shinylive_dir))[1]
    subdirs = [re.sub("^shinylive-", "", str(s)) for s in subdirs]
    return subdirs


def print_shinylive_local_info() -> None:
    print(
        f"""    Local shinylive dir:
        {get_default_shinylive_dir()}

    Installed versions:
        {", ".join(_installed_shinylive_versions())}"""
    )
