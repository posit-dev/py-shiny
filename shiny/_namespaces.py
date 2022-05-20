from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Union, List


class ResolvedId(str):
    pass


Id = Union[str, ResolvedId]


def namespaced_id(id: Id) -> Id:
    return namespaced_id_ns(id, get_current_namespaces())


def namespaced_id_ns(id: Id, namespaces: List[str] = []) -> Id:
    if isinstance(id, ResolvedId) or len(namespaces) == 0:
        return id
    else:
        return ResolvedId("_".join(namespaces) + "_" + id)


def get_current_namespaces() -> List[str]:
    return _current_namespaces.get()


_current_namespaces: ContextVar[List[str]] = ContextVar(
    "current_namespaces", default=[]
)


@contextmanager
def namespace_context(namespaces: List[str]):
    token: Token[List[str]] = _current_namespaces.set(namespaces)
    try:
        yield
    finally:
        _current_namespaces.reset(token)
