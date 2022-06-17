from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Union


class ResolvedId(str):
    def __call__(self, id: "Id") -> "ResolvedId":
        if self == "" or isinstance(id, ResolvedId):
            return ResolvedId(id)
        else:
            return ResolvedId(self + "_" + id)


Root = ResolvedId("")


Id = Union[str, ResolvedId]


def namespaced_id(id: Id) -> ResolvedId:
    return ResolvedId(get_current_namespace())(id)


def get_current_namespace() -> ResolvedId:
    return _current_namespace.get()


_current_namespace: ContextVar[ResolvedId] = ContextVar(
    "current_namespace", default=Root
)


@contextmanager
def namespace_context(id: Union[Id, None]):
    namespace = namespaced_id(id) if id else Root
    token: Token[ResolvedId] = _current_namespace.set(namespace)
    try:
        yield
    finally:
        _current_namespace.reset(token)
