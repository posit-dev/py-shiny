__all__ = ("input_handlers",)

from datetime import date, datetime
from typing import TYPE_CHECKING, Callable, Dict, Union, List, Any, TypeVar

if TYPE_CHECKING:
    from .session import Session

from .types import ActionButtonValue

InputHandlerType = Callable[[Any, str, "Session"], Any]


class _InputHandlers(Dict[str, InputHandlerType]):
    def __init__(self):
        super().__init__()

    def add(self, name: str, force: bool = False) -> Callable[[InputHandlerType], None]:
        def _(func: InputHandlerType):
            if name in self and not force:
                raise ValueError(f"Input handler {name} already registered")
            self[name] = func
            return None

        return _

    def remove(self, name: str):
        del self[name]

    def process_value(
        self, type: str, value: Any, name: str, session: "Session"
    ) -> Any:
        handler = self.get(type)
        if handler is None:
            raise ValueError("No input handler registered for type: " + type)
        return handler(value, name, session)


input_handlers = _InputHandlers()


_NumberType = TypeVar("_NumberType", int, float, None)

# Doesn't do anything since it seems weird to coerce None into some sort of NA (like we do in R)?
@input_handlers.add("shiny.number")
def _(value: _NumberType, name: str, session: "Session") -> _NumberType:
    return value


# TODO: implement when we have bookmarking
@input_handlers.add("shiny.password")
def _(value: str, name: str, session: "Session") -> str:
    return value


@input_handlers.add("shiny.date")
def _(
    value: Union[str, List[str]], name: str, session: "Session"
) -> Union[date, List[date]]:
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return [datetime.strptime(v, "%Y-%m-%d").date() for v in value]


@input_handlers.add("shiny.datetime")
def _(
    value: Union[int, float, List[int], List[float]], name: str, session: "Session"
) -> Union[datetime, List[datetime]]:
    if isinstance(value, (int, float)):
        return datetime.utcfromtimestamp(value)
    return [datetime.utcfromtimestamp(v) for v in value]


@input_handlers.add("shiny.action")
def _(value: int, name: str, session: "Session") -> ActionButtonValue:
    return ActionButtonValue(value)


# TODO: implement when we have bookmarking
@input_handlers.add("shiny.file")
def _(value: Any, name: str, session: "Session") -> Any:
    return value
