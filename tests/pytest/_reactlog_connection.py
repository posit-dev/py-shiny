"""A test client that lets reactive work settle between recorded input messages."""

from shiny._connection import MockConnection
from shiny.reactive import flush


class SettledConnection(MockConnection):
    def __init__(self) -> None:
        super().__init__()
        self._received_init = False

    async def receive(self) -> str:
        if self._received_init:
            await flush()
        message = await super().receive()
        self._received_init = True
        return message
