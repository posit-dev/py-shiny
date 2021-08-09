import json
import re
from reactives import ReactiveValues, Observer
from connmanager import Connection, ConnectionClosed
import asyncio
from typing import TYPE_CHECKING, Callable, Any, Optional
if TYPE_CHECKING:
    from shinyapp import ShinyApp


class ShinySession:
    def __init__(self, app: 'ShinyApp', id: int, conn: Connection) -> None:
        self._app: ShinyApp = app
        self.id: int = id
        self._conn: Connection = conn

        self.input: ReactiveValues = ReactiveValues()
        self.output: Outputs = Outputs(self)

        self._message_queue_in: asyncio.Queue[Optional[dict[str, Any]]] = asyncio.Queue()
        self._message_queue_out: list[dict[str, str]] = []

        self._app.server(self.input, self.output)

    async def run(self) -> None:
        # SEND {"config":{"workerId":"","sessionId":"9d55970c321d821bb2c1b28da609e60b","user":null}}
        await self._conn.send(
            json.dumps({"config": {"workerId": "", "sessionId": str(self.id), "user": None}})
        )

        # Start the producer and consumer coroutines.
        await asyncio.gather(
            self._message_queue_in_producer(),
            self._message_queue_in_consumer()
        )

        # Session has closed; unregister from the app.
        self._app.remove_session(self)


    async def _message_queue_in_producer(self) -> None:
        try:
            while True:
                message: str = await self._conn.receive()
                print("RECV: " + message)

                try:
                    msg = json.loads(message)
                except json.JSONDecodeError:
                    print("ERROR: Invalid JSON message")
                    continue

                self._message_queue_in.put_nowait(msg)

        except ConnectionClosed:
            # None is a sentinal value signalling that the connection was
            # closed. This is needed so that the consumer knows to stop.
            self._message_queue_in.put_nowait(None)


    async def _message_queue_in_consumer(self) -> None:
        while True:
            message = await self._message_queue_in.get()

            # None is a signal that the connection is closed.
            if message is None:
                return

            if message["method"] in ["init", "update"]:
                data: dict[str, Any] = message["data"]
                for (key, val) in data.items():
                    if ":" in key:
                        key = key.split(":")[0]

                    self.input[key] = val

            self.request_flush()

            await self._app.flush_pending_sessions()


    # Pending messages
    def add_message(self, message: dict[str, str]) -> None:
        self._message_queue_out.append(message)

    def get_messages(self) -> list[dict[str, str]]:
        return self._message_queue_out

    def clear_messages(self) -> None:
        self._message_queue_out.clear()

    async def send_message(self, message: dict[str, Any]) -> None:
        await self._conn.send(json.dumps(message))

    def request_flush(self) -> None:
        self._app.request_flush(self)

    async def flush(self) -> None:
        values: dict[str, str] = {}

        for value in self.get_messages():
            values.update(value)

        message: dict[str, Any] = {
            "errors": {},
            "values": values,
            "inputMessages": []
        }

        try:
            message_str: str = json.dumps(message) + "\n"
            print(
                "SEND: " + re.sub('(?m)base64,[a-zA-Z0-9+/=]+', '[base64 data]', message_str),
                end = ""
            )
            await self._conn.send(message_str)
        finally:
            self.clear_messages()



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
