# Needed for types imported only during TYPE_CHECKING with Python 3.7 - 3.9
# See https://www.python.org/dev/peps/pep-0655/#usage-in-python-3-11
from __future__ import annotations

__all__ = ("input_handlers",)

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Dict

if TYPE_CHECKING:
    from .session import Session

from .module import ResolvedId
from .types import ActionButtonValue

InputHandlerType = Callable[[Any, ResolvedId, "Session"], Any]


class _InputHandlers(Dict[str, InputHandlerType]):
    def __init__(self):
        super().__init__()

    def add(self, type: str, force: bool = False) -> Callable[[InputHandlerType], None]:
        def _(func: InputHandlerType):
            if type in self and not force:
                raise ValueError(f"Input handler {type} already registered")
            self[type] = func
            return None

        return _

    def remove(self, type: str) -> None:
        del self[type]

    def _process_value(
        self, type: str, value: Any, name: ResolvedId, session: Session
    ) -> Any:
        handler = self.get(type)
        if handler is None:
            raise ValueError("No input handler registered for type: " + type)
        return handler(value, name, session)


input_handlers: _InputHandlers = _InputHandlers()
input_handlers.__doc__ = """
Manage Shiny input handlers.

Add and/or remove input handlers of a given ``type``. Shiny uses these handlers to
pre-process input values from the client (after being deserialized) before passing them
to the ``input`` argument of an :class:`~shiny.App`'s ``server`` function.

The ``type`` is based on the ``getType()`` JavaScript method on the relevant Shiny
input binding. See `this article <https://shiny.posit.co/articles/js-custom-input.html>`_
for more information on how to create custom input bindings. (The article is about
Shiny for R, but the JavaScript and general principles are the same.)

Methods
--------
add(type: str, force: bool = False) -> Callable[[InputHandlerType], None]
    Register an input handler. This method returns a decorator that registers the
    decorated function as the handler for the given ``type``. This handler should
    accept three arguments:
    - the input ``value``
    - the input ``name``
    - the :class:`~shiny.Session` object
remove(type: str)
    Unregister an input handler.

Note
----
``add()`` ing an input handler will make it persist for the duration of the Python
process (unless Shiny is explicitly reloaded). For that reason, verbose naming is
encouraged to minimize the risk of colliding with other Shiny input binding(s) which
happen to use the same ``type`` (if the binding is bundled with a package, we
recommend the format of "packageName.widgetName").

Example
-------
```{python}
#| eval: false
from shiny.input_handler import input_handlers
@input_handlers.add("mypackage.intify")
def _(value, name, session):
    return int(value)
```

On the Javascript side, the associated input binding must have a corresponding
``getType`` method:

```{python}
#| eval: false
getType: function(el) {
    return "mypackage.intify";
}
```
"""


@input_handlers.add("shiny.date")
def _(
    value: str | list[str], name: ResolvedId, session: Session
) -> date | None | tuple[date | None, date | None]:

    if isinstance(value, str):
        return _safe_strptime_date(value)
    else:
        return (
            _safe_strptime_date(value[0]),
            _safe_strptime_date(value[1]),
        )


def _safe_strptime_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@input_handlers.add("shiny.datetime")
def _(
    value: int | float | list[int] | list[float],
    name: ResolvedId,
    session: Session,
) -> datetime | tuple[datetime, datetime]:
    def as_utc_date(x: int | float) -> datetime:
        dt = datetime.fromtimestamp(x, timezone.utc)
        # Remove hour offset from print method by removing the timezone
        # Ex: 2021-08-01T00:00:00+00:00 -> 2021-08-01T00:00:00
        # This is done as all dates are in UTC
        return dt.replace(tzinfo=None)

    if isinstance(value, (int, float)):
        return as_utc_date(value)
    return (as_utc_date(value[0]), as_utc_date(value[1]))


@input_handlers.add("shiny.action")
def _(value: int, name: ResolvedId, session: Session) -> ActionButtonValue:
    # TODO: ActionButtonValue() class can probably be removed
    return ActionButtonValue(value)


# The inputs handlers below currently do nothing, but still need to be defined,
# otherwise there will be an error when the input value is handled.


@input_handlers.add("shiny.number")
def _(value: str, name: ResolvedId, session: Session) -> str:
    return value


# TODO: implement when we have bookmarking
@input_handlers.add("shiny.password")
def _(value: str, name: ResolvedId, session: Session) -> str:
    return value


# TODO: implement when we have bookmarking
@input_handlers.add("shiny.file")
def _(value: Any, name: ResolvedId, session: Session) -> Any:
    return value
