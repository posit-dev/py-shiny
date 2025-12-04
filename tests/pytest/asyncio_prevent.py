"""This script is NOT designed to be run as part of a pytest suite; it demands a clean
Python process because it needs to be run before the shiny module is loaded.

The purpose of this script is to ensure that no shiny module initialization code uses
the event loop. The running event loop during shiny module startup is different than the
running event loop during the app's operation (I assume uvicorn creates the latter). The
creation of, say, an asyncio.Lock during the course of shiny module startup will result
in race conditions if the lock is used during the app's operation."""

if __name__ == "__main__":
    import importlib
    import sys

    if "shiny" in sys.modules:
        raise RuntimeError(
            "Bad test: shiny was already loaded, it's important that asyncio functions"
            " are patched before shiny loads"
        )

    # Patch the low-level function that all asyncio operations use to access the event loop
    # This catches all ways of accessing the event loop, not just specific functions
    from asyncio import events

    if not hasattr(events, "_get_running_loop"):
        raise RuntimeError(
            "asyncio.events._get_running_loop does not exist in this Python version. "
            "This test needs to be updated for this Python version."
        )

    def _spy_get_running_loop():
        raise RuntimeError(
            "Attempt to access asyncio event loop during module import. "
            "Asyncio objects should not be created at module level."
        )

    events._get_running_loop = _spy_get_running_loop  # type: ignore

    # Doing this instead of "import shiny" so no linter is tempted to remove it
    importlib.import_module("shiny")
    print(
        "Success; shiny module loading did not attempt to access an asyncio event "
        "loop\n",
        file=sys.stderr,
    )
