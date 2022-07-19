"""This script is NOT designed to be run as part of a pytest suite; it demands a clean
Python process because it needs to be run before the shiny module is loaded.

The purpose of this script is to ensure that no shiny module initialization code uses
the event loop. The running event loop during shiny module startup is different than the
running event loop during the app's operation (I assume uvicorn creates the latter). The
creation of, say, an asyncio.Lock during the course of shiny module startup will result
in race conditions if the lock is used during the app's operation."""

if __name__ == "__main__":
    import sys
    import asyncio
    import importlib
    from typing import Optional

    if "shiny" in sys.modules:
        raise RuntimeError(
            "Bad test: shiny was already loaded, it's important that SpyEventLoopPolicy"
            " is installed before shiny loads"
        )

    class SpyEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
        def get_event_loop(self):
            raise RuntimeError("get_event_loop called")

        def set_event_loop(self, loop: Optional[asyncio.AbstractEventLoop]):
            raise RuntimeError("set_event_loop called")

        def new_event_loop(self):
            raise RuntimeError("new_event_loop called")

    asyncio.set_event_loop_policy(SpyEventLoopPolicy())

    # Doing this instead of "import shiny" so no linter is tempted to remove it
    importlib.import_module("shiny")
    sys.stderr.write(
        "Success; shiny module loading did not attempt to access an asyncio event "
        "loop\n"
    )
