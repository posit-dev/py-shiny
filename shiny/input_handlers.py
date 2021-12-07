from datetime import datetime
from typing import TYPE_CHECKING, Callable, Dict, Union, List, Any

if TYPE_CHECKING:
    from .shinysession import ShinySession

InputHandlerType = Callable[[Any, "ShinySession", str], Any]


class _InputHandlers(Dict[str, InputHandlerType]):
    def __init__(self):
        super().__init__()

    def register(self, name: str, handler: InputHandlerType, force: bool = False):
        if name in self and not force:
            raise Exception(f"Input handler {name} already exists")
        self[name] = handler

    def unregister(self, name: str):
        del self[name]


InputHandlers = _InputHandlers()

# Doesn't do anything since it seems weird to case None to some sort of NA?
def _number_handler(value: str, session: "ShinySession", name: str):
    return value


# TODO: implement when we have bookmarking
def _password_handler(value: str, session: "ShinySession", name: str):
    return value


def _date_handler(value: Union[str, List[str]], session: "ShinySession", name: str):
    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d").date()
    return [datetime.strptime(v, "%Y-%m-%d").date() for v in value]


def _datetime_handler(
    value: Union[float, List[float]], session: "ShinySession", name: str
):
    if isinstance(value, float):
        return datetime.utcfromtimestamp(value)
    return [datetime.utcfromtimestamp(v) for v in value]


def _action_btn_handler(value: int, session: "ShinySession", name: str):
    return ActionButtonValue(value)


class ActionButtonValue(int):
    pass


# TODO: implement when we have bookmarking
def _file_handler(value: str, session: "ShinySession", name: str):
    return value


# TODO: implement shiny.password & shiny.file once we have bookmarking
InputHandlers.register("shiny.number", _number_handler)
InputHandlers.register("shiny.password", _password_handler)
InputHandlers.register("shiny.date", _date_handler)
InputHandlers.register("shiny.datetime", _datetime_handler)
InputHandlers.register("shiny.action", _action_btn_handler)
InputHandlers.register("shiny.file", _file_handler)
