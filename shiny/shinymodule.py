__all__ = (
    "ReactiveValuesProxy",
    "OutputsProxy",
    "ShinySessionProxy",
    "ShinyModule",
)

from typing import Union, Callable

from . import shinysession
from .shinysession import ShinySession, Outputs
from .reactives import ReactiveValues
from .render import RenderFunction
from .types import MISSING_TYPE, MISSING


class ReactiveValuesProxy(ReactiveValues):
    def __init__(self, ns: str, values: ReactiveValues):
        self._ns: str = ns
        self._values: ReactiveValues = values

    def _ns_key(self, key: str) -> str:
        return self._ns + "-" + key

    def __setitem__(self, key: str, value: object) -> None:
        self._values[self._ns_key(key)] = value

    def __getitem__(self, key: str) -> object:
        return self._values[self._ns_key(key)]

    def __delitem__(self, key: str) -> None:
        del self._values[self._ns_key(key)]


class OutputsProxy(Outputs):
    def __init__(self, ns: str, outputs: Outputs):
        self._ns: str = ns
        self._outputs: Outputs = outputs

    def _ns_key(self, key: str) -> str:
        return self._ns + "-" + key

    def __call__(
        self, name: str
    ) -> Callable[[Union[Callable[[], object], RenderFunction]], None]:
        return self._outputs(self._ns_key(name))


class ShinySessionProxy(ShinySession):
    def __init__(self, ns: str, parent_session: ShinySession) -> None:
        self._ns: str = ns
        self._parent: ShinySession = parent_session
        self.input: ReactiveValuesProxy = ReactiveValuesProxy(ns, parent_session.input)
        self.output: OutputsProxy = OutputsProxy(ns, parent_session.output)


class ShinyModule:
    def __init__(self, ui: object, server: Callable[[ShinySessionProxy], None]) -> None:
        self._ui: object = ui
        self._server: Callable[[ShinySessionProxy], None] = server

    def ui(self, ns: str):
        # Just a placeholder for now
        return ns

    def server(
        self, ns: str, *, session: Union[MISSING_TYPE, ShinySession] = MISSING
    ) -> None:
        self.ns: str = ns

        # Some acrobatics for the type checker
        if isinstance(session, MISSING_TYPE):
            cur_session = shinysession.get_current_session()
            if cur_session is None:
                raise ValueError("No Shiny session is active.")
            session = cur_session
        session2: ShinySession = session

        session_proxy = ShinySessionProxy(ns, session2)
        self._server(session_proxy)
