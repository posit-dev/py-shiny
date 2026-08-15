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

from collections.abc import Iterable, Mapping
from typing import Any, TypeVar, cast

# A choice value.
#
# Deliberately `Any` rather than a union of the scalar types we expect. `Mapping`'s key
# type is invariant, so a narrower annotation makes `Mapping[<narrow>, TagChild]` reject
# `dict[int, str]` or `dict[str, str]`.
ChoiceValue = Any

_V = TypeVar("_V")


def normalize_choices_indexed(
    x: Mapping[Any, _V],
) -> tuple[dict[str, _V], dict[str, Any]]:
    """
    Coerce choice values (the mapping's keys) to ``str``, preserving order.

    Returns both the stringified mapping and an index from each string form back to the
    original choice value, which :func:`resolve_selected_values` needs.

    Raises
    ------
    ValueError
        If two choice values collide once stringified. Silently dropping one of them
        would make an option disappear from the rendered group with no diagnostic.
    """
    labels: dict[str, _V] = {}
    originals: dict[str, Any] = {}

    for key, label in x.items():
        str_key = str(key)
        if str_key in labels:
            raise ValueError(
                f"Duplicate choice value {str_key!r}: {originals[str_key]!r} and {key!r} "
                "are distinct choices but are identical once converted to a string. "
                "Choice values become HTML `value` attributes, so they must be unique "
                "as strings."
            )
        labels[str_key] = label
        originals[str_key] = key

    return labels, originals


def normalize_choices_mapping(x: Mapping[Any, _V]) -> dict[str, _V]:
    """Coerce choice values (the mapping's keys) to ``str``, preserving order."""
    return normalize_choices_indexed(x)[0]


def resolve_selected_values(selected: Any, choice_values: Mapping[str, Any]) -> Any:
    """
    Replace each ``selected`` entry with the choice value it refers to.

    Usually a no-op, since ``selected`` entries normally *are* choice values. It matters
    when an entry compares equal to a choice value without stringifying identically:
    ``selected=[1.0]`` against ``choices={1: "a"}`` resolves to ``[1]``, so it both
    renders as and transmits ``"1"`` -- the value the option actually carries.
    """
    if selected is None or not choice_values:
        return selected

    originals = list(choice_values.values())

    def resolve_one(value: Any) -> Any:
        if str(value) in choice_values:
            return value
        for original in originals:
            if original == value:
                return original
        return value

    if isinstance(selected, (str, bytes)) or not isinstance(selected, Iterable):
        return resolve_one(selected)
    return [resolve_one(value) for value in cast("Iterable[Any]", selected)]


def _as_raw_list(x: Any) -> list[Any]:
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
    return [str(v) for v in _as_raw_list(x)]


def normalize_selected_scalar(x: Any) -> str | None:
    """
    Coerce ``selected`` to a single string, for clients that expect a bare scalar.

    A sequence collapses to its first element, and an empty one to ``None``.
    """
    if x is None:
        return None
    values = _as_raw_list(x)
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
    values = _as_raw_list(x)
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
    against. Entries that refer to a choice value without stringifying identically are
    handled by :func:`resolve_selected_values` before they get here.
    """

    def __init__(self, selected: Any) -> None:
        self._strings = {str(v) for v in _as_raw_list(selected)}

    def __contains__(self, choice: Any) -> bool:
        return str(choice) in self._strings

    def __bool__(self) -> bool:
        return bool(self._strings)
