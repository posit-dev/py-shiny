import json
import re
from reactives import ReactiveValues, Observer
from connmanager import Connection, ConnectionDisconnect
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from shinyapp import ShinyApp


class ShinySession:
    def __init__(self, app: 'ShinyApp', id: int, conn: Connection) -> None:
        self._app: 'ShinyApp' = app
        self.id: int = id
        self._conn: Connection = conn

        self.input: ReactiveValues = ReactiveValues()
        self.output: Outputs = Outputs(self)

        self._message_queue: list[dict[str, str]] = []

        self._app.server(self.input, self.output)

    async def serve(self) -> None:
        # SEND {"config":{"workerId":"","sessionId":"9d55970c321d821bb2c1b28da609e60b","user":null}}
        await self._conn.send(
            json.dumps({"config": {"workerId": "", "sessionId": str(self.id), "user": None}})
        )

        try:
            while True:
                message: str = await self._conn.receive()
                if not message:
                    break

                await self._handle_incoming_message(message)

        except ConnectionDisconnect:
            pass

        self._app.remove_session(self)


    # Pending messages
    def add_message(self, message: dict[str, str]) -> None:
        self._message_queue.append(message)

    def get_messages(self) -> list[dict[str, str]]:
        return self._message_queue

    def clear_messages(self) -> None:
        self._message_queue.clear()


    def request_flush(self) -> None:
        self._app.request_flush(self)

    async def flush(self) -> None:
        for message in self.get_messages():
            message: dict[str, Any] = {"errors": {}, "values": message, "inputMessages": []}

            message_str: str = json.dumps(message) + "\n"
            print(
                "SEND: " + re.sub('(?m)base64,[a-zA-Z0-9+/=]+', '[base64 data]', message_str),
                end = ""
            )
            await self._conn.send(message_str)

        self.clear_messages()


    async def _handle_incoming_message(self, message: str) -> None:
        """This is called when an incoming message arrives."""
        print("RECV: " + message)

        try:
            msg = json.loads(message)
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON message")
            return

        if msg["method"] in ["init", "update"]:
            data: dict[str, Any] = msg["data"]
            for (key, val) in data.items():
                if ":" in key:
                    key = key.split(":")[0]

                self.input[key] = val

        self.request_flush()

        await self._app.flush_pending_sessions()


class Outputs:
    def __init__(self, session: ShinySession):
        self._output_obervers: dict[str, Observer] = {}
        self._session: ShinySession = session

    def set(self, name: str):
        def set_fn(fn: Callable[[], Any]):
            if name in self._output_obervers:
                self._output_obervers[name].destroy()

            @Observer
            def obs():
                message: dict[str, str] = {}
                message[name] = fn()
                self._session.add_message(message)

            self._output_obervers[name] = obs

            return None

        return set_fn
