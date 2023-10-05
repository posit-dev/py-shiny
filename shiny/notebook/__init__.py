from __future__ import annotations

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import display, HTML
from typing import Any, cast
import asyncio
import uuid

from shiny.session import _utils as session_utils
import shiny.reactive
import shiny._namespaces

from .shiny_shim import create_kernel_session, JupyterKernelConnection
from ._mimerender import initialize as initialize_mime_render
from .log import logger

with shiny.reactive.isolate():
    isolate_context = shiny.reactive.get_current_context()
# Prevent the error that normally happens when you read a reactive with no context
shiny.reactive._core._reactive_environment._current_context.set(isolate_context)


def load_ipython_extension(ipython: InteractiveShell):
    # The `ipython` argument is the currently active `InteractiveShell`
    # instance, which can be used in any way. This allows you to register
    # new magics or aliases, for example.

    initialize_mime_render(ipython)

    sess, set_comm = create_kernel_session(uuid.uuid4().hex)
    sess = sess.make_scope(uuid.uuid4().hex)
    # Permanently set this session context. Weird, I know.
    shiny.session._utils._default_session = sess
    shiny._namespaces._default_namespace = sess.ns

    ipython.push(
        {
            "input": sess.input,
            "output": OutputReceiver(sess.output),
            "session": sess,
        }
    )

    from ipykernel.comm import Comm

    def on_client_connected(comm: Comm, msg: Any):
        logger.info("Shiny client connected")

        # Let the client know that the connection is ready
        comm.send({})
        logger.info("Setting JupyterKernelConnection")

        async def proceed():
            await set_comm(JupyterKernelConnection(comm))
            await sess._run()

        asyncio.create_task(proceed())

    ipython.kernel.comm_manager.register_target(  # pyright: ignore[reportGeneralTypeIssues]
        "shiny", on_client_connected
    )

    display(
        HTML(
            """
            <link rel="stylesheet" href="/shiny/shared/shiny.min.css" />
            <script src="/shiny/shared/jquery/jquery-3.6.0.js"></script>
            <script src="/shiny/shared/shiny.js"></script>
            <link href="/shiny/shared/bootstrap/bootstrap.min.css" rel="stylesheet"/>
            <script src="/shiny/shared/bootstrap/bootstrap.bundle.min.js"></script>
            <script src="/shiny/shared/ionrangeslider/js/ion.rangeSlider.min.js"></script>
            <link href="/shiny/shared/ionrangeslider/css/ion.rangeSlider.css" rel="stylesheet"/>
            """
        )
    )


def unload_ipython_extension(ipython: InteractiveShell):
    # If you want your extension to be unloadable, put that logic here.
    ...


def _jupyter_server_extension_points():
    """
    Returns a list of dictionaries with metadata describing
    where to find the `_load_jupyter_server_extension` function.
    """
    return [{"module": "shiny.notebook.server"}]


class OutputReceiver:
    def __init__(self, output: shiny.Outputs):
        self._output = output

    def __call__(self, render_func: Any):
        self._output(render_func)
        display(render_func)
