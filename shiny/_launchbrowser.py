import logging
import os
import webbrowser

from ._hostenv import get_proxy_url


class LaunchBrowserHandler(logging.Handler):
    """Uvicorn log reader, detects successful app startup so we can launch a browser.

    This class is ONLY used when reload mode is turned off; in the case of reload, the
    launching of the browser must be tightly coupled to the HotReloadHandler as that is
    the only way to ensure the browser is only launched at startup, not on every reload.
    """

    def __init__(self):
        logging.Handler.__init__(self)
        self._launched = False

    def emit(self, record: logging.LogRecord) -> None:
        if self._launched:
            # Ensure that we never launch a browser window twice. In non-reload
            # scenarios it probably would never happen anyway, as we're unlikely to get
            # "Application startup complete." in the logs more than once, but just in
            # case someone does choose to log that string...
            return

        if "Application startup complete." in record.getMessage():
            self._launched = True
            port = os.environ["SHINY_PORT"]
            if not port.isnumeric():
                print(
                    "SHINY_PORT environment variable not set or unusable; "
                    "--launch-browser will be ignored"
                )
                # For some reason the shiny port isn't set correctly!?
                return
            host = os.environ["SHINY_HOST"]
            url = get_proxy_url(f"http://{host}:{port}/")
            webbrowser.open(url, 1)
