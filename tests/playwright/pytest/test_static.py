import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from shiny._static import (
    _installed_shinylive_versions,
    get_default_shinylive_dir,
    remove_shinylive_local,
)


@contextmanager
def run_within_dir(path: Path) -> Generator[None, None, None]:
    """
    Utility function to run some code within a directory, and change back to the current directory afterwards.
    Example usage:
    ```
    with run_within_dir(directory):
        some_code()
    ```
    """
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def test_get_default_shinylive_dir():
    assert isinstance(get_default_shinylive_dir(), Path)


def test_remove_shinylive_local(tmp_path: Path):
    with run_within_dir(tmp_path):
        shinylive_path = Path("shinylive")
        shinylive_path.mkdir()
        assert os.path.exists(shinylive_path)
        remove_shinylive_local(shinylive_path)
        assert not os.path.exists(shinylive_path)


def test_installed_shinylive_versions(tmp_path: Path):
    with run_within_dir(tmp_path):
        Path("shinylive/shinylive-foo").mkdir(parents=True, exist_ok=True)
        Path("shinylive/shinylive-bar").mkdir(parents=True, exist_ok=True)
        Path("shinylive/shinylive-bar/nested_directory").mkdir(
            parents=True, exist_ok=True
        )

        versions = _installed_shinylive_versions(shinylive_dir=Path("shinylive"))
        assert set(versions) == {"foo", "bar"}
