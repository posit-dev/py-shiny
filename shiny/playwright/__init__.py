try:
    import playwright  # noqa: F401 # pyright: ignore[reportUnusedImport, reportMissingTypeStubs]
except ImportError:
    raise ImportError(
        "The shiny.playwright module requires the playwright package to be installed."
        " Please install it with this command:"
        "\n\n    pip install playwright"
    )
# If `pytest` is installed...
try:
    import pytest  # noqa: F401 # pyright: ignore[reportUnusedImport, reportMissingTypeStubs]

    # At this point, `playwright` and `pytest` are installed.
    # Try to make sure `pytest-playwright` is installed
    try:
        import pytest_playwright  # noqa: F401 # pyright: ignore[reportUnusedImport, reportMissingTypeStubs]

    except ImportError:
        raise ImportError(
            "If you are using pytest to test your app,"
            " you can install the pytest-playwright shim package with this command:",
            "\n\n    pip install pytest-playwright",
        )
except ImportError:
    pass
from . import controller, expect

__all__ = ["expect", "controller"]
