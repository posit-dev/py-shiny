import react
from reactives import ReactiveValues, Observer

class ShinySession:
    def __init__(self, server: callable) -> None:
        self._message_queue = []

        self.input = ReactiveValues()
        self.output = Outputs(self)
        self._server = server

        self._server(self.input, self.output)

    # Pending messages
    def add_message(self, message):
        self._message_queue.append(message)

    def get_messages(self):
        return self._message_queue

    def clear_messages(self):
        self._message_queue = []


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

