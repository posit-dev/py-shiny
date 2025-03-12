from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import orjson


# https://github.com/rstudio/shiny/blob/f55c26af4a0493b082d2967aca6d36b90795adf1/R/server.R#L510-L514
def in_shiny_server() -> bool:
    shiny_port = os.environ.get("SHINY_PORT")
    if shiny_port is None or shiny_port == "":
        return False

    return True


def to_json_str(x: Any) -> str:
    return orjson.dumps(x).decode()


def from_json_str(x: str) -> Any:
    return orjson.loads(x)


# When saving to a file, use plain text json.
# (It's possible that we could store bytes, but unknown if there's any security benefit.)
#
# This makes the file contents independent of the json library used and
# independent of the python version being used
# (ex: pickle files are not compatible between python versions)
def to_json_file(x: Any, file: Path) -> None:
    file.write_text(to_json_str(x), encoding="utf-8")


def from_json_file(file: Path) -> Any:
    return from_json_str(file.read_text(encoding="utf-8"))
