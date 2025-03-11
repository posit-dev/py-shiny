from __future__ import annotations

import os
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
