# from jupyter_server.base.handlers import JupyterHandler
import os
import tempfile
from pathlib import Path

import tornado
from jupyter_server.serverapp import ServerApp

shiny_path = Path(__file__).parent.parent.parent
print(shiny_path / "www" / "shared")

tmpdir = tempfile.TemporaryDirectory(prefix="shiny-dependencies-")

os.environ["SHINY_JUPYTERLAB_SERVER_EXTENSION"] = "1"
# Subprocesses will dump their dependencies here. Seems really messy but I'm not sure
# what else to do. Maybe they should just put symlinks here?? (On non-Windows?)
os.environ["SHINY_JUPYTERLAB_SERVER_EXTENSION_ROOT"] = tmpdir.name


def _load_jupyter_server_extension(nb_server_app: ServerApp):
    nb_server_app.web_app.add_handlers(
        # Add the shiny package's 'static' subdirectory as a static file directory on the
        # URL path /shiny/shared
        r".*",
        [
            (
                r"/shiny/shared/(.*)",
                tornado.web.StaticFileHandler,
                {"path": shiny_path / "www" / "shared"},
            ),
            (
                r"/shiny/dependencies/(.*)",
                tornado.web.StaticFileHandler,
                {"path": tmpdir.name},
            ),
        ],
    )


# class MyExtensionHandler(JupyterHandler):
#     @tornado.web.authenticated
#     def get(self):
#         ...

#     @tornado.web.authenticated
#     def post(self):
#         ...
