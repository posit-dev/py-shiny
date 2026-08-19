"""
Shared normalization utilities for the choice-based inputs (checkbox group,
radio buttons, select, selectize, toolbar select).

Choice values become HTML ``value`` attributes, so the client only ever sees their
string form. Everything here exists to make the server and client agree: choice values
are coerced to ``str`` once, and ``selected`` is coerced the same way so that the
regenerated options markup and the ``value`` sent in an ``update_*()`` message match
by construction.

See https://github.com/posit-dev/py-shiny/issues/2272 and
https://github.com/posit-dev/py-shiny/pull/2420 for details.
"""

from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping
from typing import Any, Literal, TypeVar, Union, cast

# A choice value. The client only ever sees ``str(value)``, so these are the types with
# an unambiguous string form -- the ones the choice inputs document and test.
ChoiceValue = Union[str, int, float, bool, None]

# A choice value in a `Mapping` key position, which has to stay `Any`: `Mapping`'s key
# type is invariant, so `Mapping[ChoiceValue, TagChild]` rejects `dict[int, str]` -- and
# even `dict[str, str]`. The runtime contract is the same as `ChoiceValue`.
ChoiceKey = Any

# What a normalized mapping's keys hold. A select input's `choices` maps optgroup labels
# alongside choice values, so its top level holds both.
ChoiceKeyKind = Literal["choice value", "choice value or optgroup label"]

_DUPLICATE_KEY_REASONS: dict[ChoiceKeyKind, str] = {
    "choice value": (
        "Choice values become HTML `value` attributes, so they must be unique as "
        "strings."
    ),
    "choice value or optgroup label": (
        "A select input's `choices` holds choice values and optgroup labels in one "
        "mapping, so both must be unique as strings."
    ),
}

V = TypeVar("V")


def normalize_choices_mapping(
    x: Mapping[Any, V], *, keys_are: ChoiceKeyKind = "choice value"
) -> dict[str, V]:
    """
    Coerce choice values (the mapping's keys) to ``str``, preserving order.

    Raises
    ------
    ValueError
        If two keys collide once stringified. The normalized form is a ``dict`` keyed by
        the string form, so one of the two entries would otherwise disappear from the
        rendered input with no diagnostic.
    """
    normalized: dict[str, V] = {}
    originals: dict[str, Any] = {}

    for key, label in x.items():
        str_key = str(key)
        if str_key in normalized:
            raise ValueError(
                f"Duplicate {keys_are} {str_key!r}: {originals[str_key]!r} and {key!r} "
                f"are distinct but are identical once converted to a string. "
                + _DUPLICATE_KEY_REASONS[keys_are]
            )
        normalized[str_key] = label
        originals[str_key] = key

    return normalized


def resolve_selected(selected: Any, choice_values: Collection[str]) -> Any:
    """
    Replace each ``selected`` entry with the string form of the choice value it names.

    Matching is on the string form, since that is the only thing the client can match
    against, so a ``selected`` of ``True`` does not name the choice value ``1``. An
    integral ``float`` is the one exception: it also matches the integer it equals, so
    ``selected=[1.0]`` against ``choices={1: "a"}`` resolves to ``"1"``, the value the
    option actually carries. (R Shiny gets that case for free, since
    ``as.character(1.0)`` is ``"1"``.)

    An entry that names no choice passes through as its own string form, so an
    ``update_*()`` message still carries what the caller asked for.
    """
    if selected is None:
        return None

    def resolve_one(value: Any) -> str:
        as_str = str(value)
        if as_str in choice_values:
            return as_str
        # `str(1.0)` is `"1.0"`, so an integral float misses the `1` it names. `bool` is
        # a subclass of `int` rather than `float`, so `True` stays `"True"` here.
        if isinstance(value, float) and value.is_integer():
            as_int = str(int(value))
            if as_int in choice_values:
                return as_int
        return as_str

    if isinstance(selected, (str, bytes)) or not isinstance(selected, Iterable):
        return resolve_one(selected)
    return [resolve_one(value) for value in cast("Iterable[Any]", selected)]


def as_raw_list(x: Any) -> list[Any]:
    """
    Coerce ``selected`` to a list of raw (un-stringified) choice values.

    ``str`` and ``bytes`` are iterable but represent a single choice, so they are
    treated as scalars. Any other iterable, including the ``dict_keys``, ``set``, and
    generator shapes that a caller may build a selection from, is consumed as a
    sequence. Handling them here keeps them from falling into the scalar branch, where
    they would be stringified to their unusable ``repr``.
    """
    if x is None:
        return []
    elif isinstance(x, (str, bytes)) or not isinstance(x, Iterable):
        return [x]
    else:
        return list(cast("Iterable[Any]", x))


def normalize_selected(x: Any) -> str | list[str] | None:
    """
    Coerce ``selected`` to string(s), preserving scalar vs. sequence shape.

    Shape matters on the wire: the checkbox group's client-side ``setValue()`` expects
    an array while the radio group's expects a scalar, so a scalar ``selected`` must not
    grow into a list on its way out. Tuples become lists purely for payload consistency
    (``json.dumps()`` already serializes a tuple as a JSON array).
    """
    if x is None:
        return None
    elif isinstance(x, str):
        return x
    elif isinstance(x, bytes) or not isinstance(x, Iterable):
        return str(x)
    else:
        return [str(v) for v in cast("Iterable[Any]", x)]


def normalize_selected_list(x: Any) -> list[str] | None:
    """Coerce ``selected`` to a list of strings, for clients that expect an array."""
    if x is None:
        return None
    return [str(v) for v in as_raw_list(x)]


def normalize_selected_scalar(x: Any) -> str | None:
    """
    Coerce ``selected`` to a single string, for clients that expect a bare scalar.

    A sequence collapses to its first element, and an empty one to ``None``.
    """
    if x is None:
        return None
    values = as_raw_list(x)
    if not values:
        return None
    return str(values[0])


def normalize_selected_radio(x: Any) -> str | list[str] | None:
    """
    Coerce ``selected`` for the radio-button binding, which expects a scalar and
    throws on a non-empty array.

    A one-element sequence unwraps to that element. An empty sequence stays ``[]``,
    which clears the selection (returning ``None`` instead would drop ``value``
    from the message and leave the previous selection in place).

    Raises
    ------
    ValueError
        If the sequence holds more than one value.
    """
    if x is None:
        return None
    values = as_raw_list(x)
    if not values:
        return []
    if len(values) > 1:
        raise ValueError(
            f"`selected` must name a single choice for a radio button group, but "
            f"{len(values)} were given: {values!r}. Pass one value, or `[]` to clear "
            "the selection."
        )
    return str(values[0])


class ChoiceSelection:
    """
    Tests whether a choice value is selected: ``choice_value in selection``.

    Comparison is on the string form, since that is the only thing the client can match
    against. Entries that name a choice value without stringifying identically are
    handled by :func:`resolve_selected` before they get here.
    """

    def __init__(self, selected: Any) -> None:
        self._strings = {str(v) for v in as_raw_list(selected)}

    def __contains__(self, choice: Any) -> bool:
        return str(choice) in self._strings

    def __bool__(self) -> bool:
        return bool(self._strings)
