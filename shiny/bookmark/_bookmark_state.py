from __future__ import annotations

import os
from pathlib import Path

shiny_bookmarks_folder_name = "shiny_bookmarks"


def _local_dir(id: str) -> Path:
    # Try to save/load from current working directory as we do not know where the
    # app file is located
    return Path(os.getcwd()) / shiny_bookmarks_folder_name / id


async def local_save_dir(id: str) -> Path:
    state_dir = _local_dir(id)
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir


async def local_restore_dir(id: str) -> Path:
    return _local_dir(id)
