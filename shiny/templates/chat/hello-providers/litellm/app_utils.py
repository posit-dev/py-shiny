import os
from pathlib import Path
from typing import Any

app_dir = Path(__file__).parent
env_file = app_dir / ".env"


def load_dotenv(dotenv_path: os.PathLike[str] = env_file, **kwargs: Any) -> None:
    """
    A convenience wrapper around `dotenv.load_dotenv` that warns if `dotenv` is not installed.
    It also returns `None` to make it easier to ignore the return value.
    """
    try:
        import dotenv

        dotenv.load_dotenv(dotenv_path=dotenv_path, **kwargs)
    except ImportError:
        import warnings

        warnings.warn(
            "Could not import `dotenv`. If you want to use `.env` files to "
            "load environment variables, please install it using "
            "`pip install python-dotenv`.",
            stacklevel=2,
        )
