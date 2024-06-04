try:
    import playwright  # noqa: F401 # pyright: ignore[reportUnusedImport, reportMissingTypeStubs]
except ImportError:
    raise ImportError(
        "The shiny.playwright module requires the playwright package to be installed."
        " Please install it with this command:"
        "\n\n    pip install playwright"
        "\n\n",
        "If you are using pytest to test your code,"
        " you can install the pytest-playwright shim package with this command:",
        "\n\n    pip install pytest-playwright",
    )

from . import controls, expect

__all__ = ["expect", "controls"]
