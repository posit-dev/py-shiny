import react
from reactives import ReactiveValues

class Outputs:
    def __init__(self):
        self._fns = {}

    def set(self, name):
        print("add", name)
        def add_fn(fn):
            self._fns[name] = fn
            return None

        return add_fn

    def get(self, name):
        return self._fns[name]



class ShinySession:
    def __init__(self, server: callable) -> None:
        self.input = ReactiveValues()
        self.output = Outputs()
        self._server = server

        self._server(self.input, self.output)
