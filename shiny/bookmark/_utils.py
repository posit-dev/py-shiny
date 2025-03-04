import os
from typing import Any

import orjson


def is_hosted() -> bool:
    # Can't look at SHINY_PORT, as we already set it in shiny/_main.py's `run_app()`

    # TODO: Support shinyapps.io or use `SHINY_PORT` how R-shiny did

    # Instead, looking for the presence of the environment variable that Connect sets
    # (*_Connect) or Shiny Server sets (SHINY_APP)
    for env_var in ("POSIT_CONNECT", "RSTUDIO_CONNECT", "SHINY_APP"):
        if env_var in os.environ:
            return True
    return False


def to_json_str(x: Any) -> str:
    return orjson.dumps(x).decode()


def from_json_str(x: str) -> Any:
    return orjson.loads(x)
