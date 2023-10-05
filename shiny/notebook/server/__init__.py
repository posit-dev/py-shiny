# from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.serverapp import ServerApp
import tornado
from pathlib import Path
import os

shiny_path = Path(__file__).parent.parent.parent
print(shiny_path / "www" / "shared")


os.environ["SHINY_JUPYTERLAB_SERVER_EXTENSION"] = "1"


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
            )
        ],
    )


# class MyExtensionHandler(JupyterHandler):
#     @tornado.web.authenticated
#     def get(self):
#         ...

#     @tornado.web.authenticated
#     def post(self):
#         ...
