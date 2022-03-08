__all__ = ("Module", "namespaced_id")

from typing import Any, Callable, Optional

from htmltools import TagChildArg

from ._docstring import add_example
from ._namespaces import namespaced_id
from .session import Inputs, Outputs, Session, require_active_session, session_context


class ModuleInputs(Inputs):
    """
    A class representing a module's outputs.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.modules.Module`'s ``server`` function. For this reason, you
    shouldn't need to create instances of this class yourself. Furthermore, you
    probably shouldn't need this class for type checking either since it has the same
    signature as :class:`shiny.session.Session`.
    """

    def __init__(self, ns: str, parent_inputs: Inputs):
        self._ns = namespaced_id(ns, parent_inputs._ns)  # Support nested modules
        # Don't set _parent attribute like the other classes since Inputs redefines
        # __setattr__
        self._map = parent_inputs._map


class ModuleOutputs(Outputs):
    """
    A class representing a module's outputs.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.modules.Module`'s ``server`` function. For this reason, you
    shouldn't need to create instances of this class yourself. Furthermore, you
    probably shouldn't need this class for type checking either since it has the same
    signature as :class:`shiny.session.Session`.
    """

    def __init__(self, ns: str, parent_outputs: Outputs):
        self._ns = namespaced_id(ns, parent_outputs._ns)  # Support nested modules
        self._parent = parent_outputs

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._parent, attr)


class ModuleSession(Session):
    """
    A class representing a module's outputs.

    Warning
    -------
    An instance of this class is created for each request and passed as an argument to
    the :class:`shiny.modules.Module`'s ``server`` function. For this reason, you
    shouldn't need to create instances of this class yourself. Furthermore, you
    probably shouldn't need this class for type checking either since it has the same
    signature as :class:`shiny.session.Session`.
    """

    def __init__(self, ns: str, parent_session: Session):
        self._ns: str = namespaced_id(ns, parent_session._ns)  # Support nested modules
        self._parent: Session = parent_session
        self.input: ModuleInputs = ModuleInputs(ns, parent_session.input)
        self.output: ModuleOutputs = ModuleOutputs(ns, parent_session.output)

    def __getattr__(self, attr: str) -> Any:
        return getattr(self._parent, attr)


class MockModuleSession(ModuleSession):
    def __init__(self, ns: str):
        self._ns = ns


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

        # Create a fake session so that namespaced_id() knows
        # what the relevant namespace is
        with session_context(MockModuleSession(ns)):
            return self._ui(*args)

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

        mod_sess = ModuleSession(ns, require_active_session(session))
        with session_context(mod_sess):
            return self._server(mod_sess.input, mod_sess.output, mod_sess)
