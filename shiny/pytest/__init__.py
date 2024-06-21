try:
    import pytest  # noqa: F401 # pyright: ignore[reportUnusedImport, reportMissingTypeStubs]
except ImportError:
    raise ImportError(
        "The shiny.pytest module requires the pytest package to be installed."
        " Please install it with this command:"
        "\n\n    pip install pytest"
    )

from ._fixture import ScopeName, create_app_fixture

__all__ = ("create_app_fixture", "ScopeName")
