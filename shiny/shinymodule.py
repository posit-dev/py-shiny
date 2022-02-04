__all__ = (
    "InputsProxy",
    "InputsProxy",
    "OutputsProxy",
    "SessionProxy",
    "ShinyModule",
)

from typing import Any, Callable, Optional

from htmltools.core import TagChildArg

from .reactive import Value
from .render import RenderFunction
from .session import Inputs, Outputs, Session, _require_active_session


class InputsProxy(Inputs):
    def __init__(self, ns: str, values: Inputs):
        self._ns: str = ns
        self._values: Inputs = values

    def _ns_key(self, key: str) -> str:
        return self._ns + "-" + key

    def __setitem__(self, key: str, value: Value[Any]) -> None:
        self._values[self._ns_key(key)].set(value)

    def __getitem__(self, key: str) -> Value[Any]:
        return self._values[self._ns_key(key)]

    def __delitem__(self, key: str) -> None:
        del self._values[self._ns_key(key)]

    # Allow access of values as attributes.
    def __setattr__(self, attr: str, value: Value[Any]) -> None:
        if attr in ("_values", "_ns", "_ns_key"):
            object.__setattr__(self, attr, value)
            return
        else:
            self.__setitem__(attr, value)

    def __getattr__(self, attr: str) -> Value[Any]:
        if attr in ("_values", "_ns", "_ns_key"):
            return object.__getattribute__(self, attr)
        else:
            return self.__getitem__(attr)

    def __delattr__(self, key: str) -> None:
        self.__delitem__(key)


class OutputsProxy(Outputs):
    def __init__(self, ns: str, outputs: Outputs):
        self._ns: str = ns
        self._outputs: Outputs = outputs

    def _ns_key(self, key: str) -> str:
        return self._ns + "-" + key

    def __call__(
        self, *, name: Optional[str] = None
    ) -> Callable[[RenderFunction], None]:
        return self._outputs(name=self._ns_key(name))


class SessionProxy(Session):
    def __init__(self, ns: str, parent_session: Session) -> None:
        self._ns: str = ns
        self._parent: Session = parent_session
        self.input: InputsProxy = InputsProxy(ns, parent_session.input)
        self.output: OutputsProxy = OutputsProxy(ns, parent_session.output)


class ShinyModule:
    def __init__(
        self,
        ui: Callable[..., TagChildArg],
        server: Callable[[InputsProxy, OutputsProxy, SessionProxy], None],
    ) -> None:
        self._ui: Callable[..., TagChildArg] = ui
        self._server: Callable[[InputsProxy, OutputsProxy, SessionProxy], None] = server

    def ui(self, namespace: str, *args: Any) -> TagChildArg:
        ns = ShinyModule._make_ns_fn(namespace)
        return self._ui(ns, *args)

    def server(self, ns: str, *, session: Optional[Session] = None) -> None:
        self.ns: str = ns
        session = _require_active_session(session)
        session_proxy = SessionProxy(ns, session)
        self._server(session_proxy.input, session_proxy.output, session_proxy)

    @staticmethod
    def _make_ns_fn(namespace: str) -> Callable[[str], str]:
        def ns_fn(id: str) -> str:
            return namespace + "-" + id

        return ns_fn
