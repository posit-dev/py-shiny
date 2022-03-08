# TODO: make this available under the shiny.modules API
__all__ = ("namespaced_id",)

from typing import Union, Optional

from .types import MISSING, MISSING_TYPE


def namespaced_id(id: str, ns: Union[str, MISSING_TYPE, None] = MISSING) -> str:
    """
    Namespace an ID based on the current ``Module()``'s namespace.

    Parameters
    ----------
    id
        The ID to namespace..
    """
    if isinstance(ns, MISSING_TYPE):
        ns = get_current_namespace()

    if ns is None:
        return id
    else:
        return ns + "_" + id


def get_current_namespace() -> Optional[str]:
    from .session import get_current_session

    session = get_current_session()
    if session is None:
        return None
    else:
        return session._ns
