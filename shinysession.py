import json
from reactives import ReactiveValues, Observer
from iomanager import IOHandle

class ShinySession:
    def __init__(self, app: 'ShinyApp', id: int, iohandle: IOHandle) -> None:
        self._app = app
        self.id: int = id
        self._iohandle = iohandle

        self.input = ReactiveValues()
        self.output = Outputs(self)

        self._message_queue: list[str] = []

        self._app.server(self.input, self.output)

    # Pending messages
    def add_message(self, message: str):
        self._message_queue.append(message)

    def get_messages(self) -> list[str]:
        return self._message_queue

    def clear_messages(self) -> None:
        self._message_queue.clear()


    def request_flush(self) -> None:
        self._app.request_flush(self)

    async def flush(self) -> None:
        for message in self.get_messages():
            message_str = json.dumps(message) + "\n"
            print("SEND: " + message_str, end = "")
            await self._iohandle.send(message_str)

        self.clear_messages()


    async def handle_incoming_message(self, message: str) -> None:
        """This is called by the iohandle when an incoming message arrives."""
        print("RECV: " + message)

        vals = json.loads(message)
        for (key, val) in vals.items():
            self.input[key] = val

        self.request_flush()

        await self._app.flush_pending_sessions()


class Outputs:
    def __init__(self, session: ShinySession):
        self._output_obervers = {}
        self._session = session

    def set(self, name):
        def set_fn(fn):
            if name in self._output_obervers:
                self._output_obervers[name].destroy()

            @Observer
            def obs():
                message = {}
                message[name] = fn()
                self._session.add_message(message)

            self._output_obervers[name] = obs

            return None

        return set_fn

    def get(self, name):
        return self._fns[name]

