__all__ = ("Module",)

from typing import Any, Callable, Optional

from htmltools import TagChildArg

from ._docstring import add_example
from .reactive import Value
from .render import RenderFunction
from .session import Inputs, Outputs, Session, require_active_session, session_context


class ModuleInputs(Inputs):
    """
    A class representing the inputs of a module.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.modules.Module`'s ``server`` function. For this reason, you
    shouldn't need to create instances of this class yourself. Furthermore, you
    probably shouldn't need this class for type checking either since it has the same
    signature as :class:`shiny.session.Session`.
    """

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
    """
    A class representing the outputs of a module.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.modules.Module`'s ``server`` function. For this reason, you
    shouldn't need to create instances of this class yourself. Furthermore, you
    probably shouldn't need this class for type checking either since it has the same
    signature as :class:`shiny.session.Session`.
    """

    def __init__(self, ns: str, outputs: Outputs):
        self._ns: str = ns
        self._outputs: Outputs = outputs

    def _ns_key(self, key: str) -> str:
        return self._ns + "-" + key

    def __call__(
        self,
        *,
        id: Optional[str] = None,
        suspend_when_hidden: bool = True,
        priority: int = 0,
        name: Optional[str] = None,
    ) -> Callable[[RenderFunction], None]:
        if name is not None:
            from . import _deprecated

            _deprecated._warn_deprecated(
                "`@output(name=...)` is deprecated. Use `@output(id=...)` instead."
            )
            id = name

        def set_fn(fn: RenderFunction) -> None:
            output_name = id or fn.__name__
            output_name = self._ns_key(output_name)
            out_fn = self._outputs(
                name=output_name,
                suspend_when_hidden=suspend_when_hidden,
                priority=priority,
            )
            return out_fn(fn)

        return set_fn


class ModuleSession(Session):
    """
    A class representing the session of a module.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.modules.Module`'s ``server`` function. For this reason, you
    shouldn't need to create instances of this class yourself. Furthermore, you
    probably shouldn't need this class for type checking either since it has the same
    signature as :class:`shiny.session.Session`.
    """

    def __init__(self, ns: str, parent_session: Session) -> None:
        self._ns: str = ns
        self._parent: Session = parent_session
        self.input: ModuleInputs = ModuleInputs(ns, parent_session.input)
        self.output: ModuleOutputs = ModuleOutputs(ns, parent_session.output)

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._parent, attr)


@add_example()
class Module:
    """
    Modularize UI and server-side logic.

    Parameters
    ----------
    ui
        The module's UI definition.
    server
        The module's server-side logic.
    """

    def __init__(
        self,
        ui: Callable[..., TagChildArg],
        server: Callable[[ModuleInputs, ModuleOutputs, ModuleSession], None],
    ) -> None:
        self._ui: Callable[..., TagChildArg] = ui
        self._server: Callable[
            [ModuleInputs, ModuleOutputs, ModuleSession], None
        ] = server

    def ui(self, ns: str, *args: Any) -> TagChildArg:
        """
        Render the module's UI.

        Parameters
        ----------
        namespace
            A namespace for the module.
        args
            Additional arguments to pass to the module's UI definition.
        """
        return self._ui(Module._make_ns_fn(ns), *args)

    def server(self, ns: str, *, session: Optional[Session] = None) -> None:
        """
        Invoke the module's server-side logic.

        Parameters
        ----------
        ns
            A namespace for the module.
        session
            A :class:`~shiny.Session` instance. If not provided, it is inferred via
            :func:`~shiny.session.get_current_session`.
        """
        self.ns: str = ns
        session = require_active_session(session)
        session_proxy = ModuleSession(ns, session)
        with session_context(session_proxy):
            self._server(session_proxy.input, session_proxy.output, session_proxy)

    @staticmethod
    def _make_ns_fn(namespace: str) -> Callable[[str], str]:
        def ns_fn(id: str) -> str:
            return namespace + "-" + id

        return ns_fn
