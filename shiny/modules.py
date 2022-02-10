__all__ = (
    "ModuleInputs",
    "ModuleOutputs",
    "ModuleSession",
    "Module",
)

from typing import Any, Callable, Optional

from htmltools.core import TagChildArg

from .reactive import Value
from .render import RenderFunction
from .session import Inputs, Outputs, Session
from .session._utils import require_active_session


class ModuleInputs(Inputs):
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


class ModuleOutputs(Outputs):
    def __init__(self, ns: str, outputs: Outputs):
        self._ns: str = ns
        self._outputs: Outputs = outputs

    def _ns_key(self, key: str) -> str:
        return self._ns + "-" + key

    def __call__(
        self,
        *,
        name: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0
    ) -> Callable[[RenderFunction], None]:
        def set_fn(fn: RenderFunction) -> None:
            fn_name = name or fn.__name__
            fn_name = self._ns_key(fn_name)
            out_fn = self._outputs(
                name=fn_name, suspend_when_hidden=suspend_when_hidden, priority=priority
            )
            return out_fn(fn)

        return set_fn


class ModuleSession(Session):
    def __init__(self, ns: str, parent_session: Session) -> None:
        self._ns: str = ns
        self._parent: Session = parent_session
        self.input: ModuleInputs = ModuleInputs(ns, parent_session.input)
        self.output: ModuleOutputs = ModuleOutputs(ns, parent_session.output)


class Module:
    def __init__(
        self,
        ui: Callable[..., TagChildArg],
        server: Callable[[ModuleInputs, ModuleOutputs, ModuleSession], None],
    ) -> None:
        self._ui: Callable[..., TagChildArg] = ui
        self._server: Callable[
            [ModuleInputs, ModuleOutputs, ModuleSession], None
        ] = server

    def ui(self, namespace: str, *args: Any) -> TagChildArg:
        ns = Module._make_ns_fn(namespace)
        return self._ui(ns, *args)

    def server(self, ns: str, *, session: Optional[Session] = None) -> None:
        self.ns: str = ns
        session = require_active_session(session)
        session_proxy = ModuleSession(ns, session)
        self._server(session_proxy.input, session_proxy.output, session_proxy)

    @staticmethod
    def _make_ns_fn(namespace: str) -> Callable[[str], str]:
        def ns_fn(id: str) -> str:
            return namespace + "-" + id

        return ns_fn
