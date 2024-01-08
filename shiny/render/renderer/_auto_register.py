from __future__ import annotations

from typing import Protocol, cast

# from ...session import require_active_session


class AutoRegisterP(Protocol):
    __name__: str
    _auto_registered: bool = False


class AutoRegisterMixin:
    """
    Auto registers the rendering method then the renderer is called.

    When `@output` is called on the renderer, the renderer is automatically un-registered via `._on_register()`.
    """

    _auto_registered: bool = False

    def _on_register(self: AutoRegisterP) -> None:
        if self._auto_registered:
            # We're being explicitly registered now. Undo the auto-registration.
            # (w/ module support)
            from ...session import require_active_session

            session = require_active_session(None)
            ns_name = session.output._ns(self.__name__)
            session.output.remove(ns_name)
            self._auto_registered = False

    def _auto_register(self) -> None:
        # If in Express mode, register the output
        if not self._auto_registered:
            from ...session import get_current_session

            s = get_current_session()
            if s is not None:
                from ._renderer import RendererBase

                # Cast to avoid circular import as this mixin is ONLY used within RendererBase
                renderer_self = cast(RendererBase, self)
                s.output(renderer_self)
                # We mark the fact that we're auto-registered so that, if an explicit
                # registration now occurs, we can undo this auto-registration.
                self._auto_registered = True
