from __future__ import annotations

import asyncio
import uuid
from typing import Any, cast

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
from IPython.core.interactiveshell import InteractiveShell
from IPython.display import display

import shiny._namespaces
import shiny.reactive
from shiny.session import _utils as session_utils

from ._mimerender import initialize as initialize_mime_render
from .shiny_shim import JupyterKernelConnection, create_kernel_session

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
    # Oh goodness. This is a hack to get any registered output to be display()'ed with
    # its default output.
    sess.output = OutputReceiver(sess.output)  # type: ignore

    ipython.push(
        {
            "input": sess.input,
            "output": sess.output,
            "session": sess,
        }
    )

    from comm import create_comm, get_comm_manager

    # def on_client_connected(comm: Comm, msg: Any):
    #     logger.info("Shiny client connected")

    #     # Let the client know that the connection is ready
    #     comm.send({})
    #     logger.info("Setting JupyterKernelConnection")

    #     async def proceed():
    #         await set_comm(JupyterKernelConnection(comm))
    #         await sess._run()

    #     asyncio.create_task(proceed())

    # ipython.kernel.comm_manager.register_target(  # pyright: ignore[reportGeneralTypeIssues]
    #     "shiny", on_client_connected
    # )
    comm = create_comm(target_name="shiny-kernel", data={})
    get_comm_manager().register_comm(comm)
    comm.send("{}")

    async def proceed():
        await set_comm(JupyterKernelConnection(comm))
        await sess._run()

    asyncio.create_task(proceed())

    ipython.ast_node_interactivity = "all"
    print('Setting InteractiveShell.ast_node_interactivity="all"')
    print("Shiny is running")


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
        # Set suspend_when_hidden=False because it's much harder for us to keep track of
        # what's shown and what's hidden in Jupyter notebooks.
        self._output(suspend_when_hidden=False)(render_func)
        display(render_func.default_ui(render_func.__name__))
