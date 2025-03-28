from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict

from .bookmark import serializer_unserializable
from .bookmark._serializers import can_serialize_input_file, serializer_file_input

if TYPE_CHECKING:
    from .session import Session

from .module import ResolvedId
from .types import ActionButtonValue

__all__ = ("input_handlers",)

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

See Also
--------
* :class:`~shiny.session.Inputs`'s `.set_serializer(info: InputSerializerInfo)` method for determining how an object can be serialized for bookmarking.
"""


@input_handlers.add("shiny.date")
def _(
    value: str | list[str] | None, name: ResolvedId, session: Session
) -> date | None | tuple[date | None, date | None]:

    if isinstance(value, str) or value is None:
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


@input_handlers.add("shiny.password")
def _(value: str, name: ResolvedId, session: Session) -> str:
    # Never bookmark passwords
    session.input.set_serializer(name, serializer_unserializable)

    return value


@input_handlers.add("shiny.file")
def _(value: Any, name: ResolvedId, session: Session) -> Any:

    # This function is only used when restoring a Shiny ui.input_file.
    # When a file is uploaded the usual way, it takes a different code path and won't
    # hit this function.
    if value is None:
        return None

    if not can_serialize_input_file(session):
        raise ValueError(
            "`shiny.ui.input_file()` is attempting to restore bookmark state. "
            'However the App\'s `bookmark_store=` is not set to `"server"`. '
            "Either exclude the input value (`session.bookmark.exclude.append(NAME)`) "
            'or set `bookmark_store="server"`.'
        )

    value_obj = value

    # Convert from:
    # `{name: (n1, n2, n3), size: (s1, s2, s3), type: (t1, t2, t3), datapath: (d1, d2, d3)}`
    # to:
    # `[{name: n1, size: s1, type: t1, datapath: d1}, ...]`
    value_list: list[dict[str, str | int | None]] = []
    for i in range(len(value_obj["name"])):
        value_list.append(
            {
                "name": value_obj["name"][i],
                "size": value_obj["size"][i],
                "type": value_obj["type"][i],
                "datapath": value_obj["datapath"][i],
            }
        )

    # Validate the input value
    for value_item in value_list:
        if value_item["datapath"] is not None:
            if not isinstance(value_item["datapath"], str):
                raise ValueError(
                    "Invalid type for file input path: ", type(value_item["datapath"])
                )
            if Path(value_item["datapath"]).name != value_item["datapath"]:
                raise ValueError("Invalid '/' found in file input path.")

    import shutil
    import tempfile

    from shiny._utils import rand_hex

    from .bookmark._restore_state import get_current_restore_context
    from .session import session_context

    with session_context(session):
        restore_ctx = get_current_restore_context()

    # These should not fail as we know
    if restore_ctx is None or restore_ctx.dir is None:
        raise RuntimeError("No restore context found. Cannot restore file input.")

    restore_ctx_dir = Path(restore_ctx.dir)

    if len(value_list) > 0:
        tempdir_root = tempfile.TemporaryDirectory()
        session.on_ended(lambda: tempdir_root.cleanup())

        for f in value_list:
            assert f["datapath"] is not None and isinstance(f["datapath"], str)

            data_path = f["datapath"]

            # Prepend the persistent dir
            old_file = restore_ctx_dir / data_path

            # Copy the original file to a new temp dir, so that a restored session can't
            # modify the original.
            tempdir = Path(tempdir_root.name) / rand_hex(12)
            tempdir.mkdir(parents=True, exist_ok=True)
            f["datapath"] = str(tempdir / Path(data_path).name)
            shutil.copy2(old_file, f["datapath"])

    # Need to mark this input value with the correct serializer. When a file is
    # uploaded the usual way (instead of being restored), this occurs in
    # session$`@uploadEnd`.
    session.input.set_serializer(name, serializer_file_input)

    return value_list
