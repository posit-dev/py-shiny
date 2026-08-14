"""
Shared normalization for the choice-based inputs (checkbox group, radio buttons,
select, selectize, toolbar select).

Choice values become HTML ``value`` attributes, so the client only ever sees their
string form. Everything here exists to make the server agree with that: choice values
are coerced to ``str`` once, and ``selected`` is coerced the same way so that the
regenerated options markup and the ``value`` sent in an ``update_*()`` message match
by construction.

See https://github.com/posit-dev/py-shiny/issues/2272.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, TypeVar, cast

# A choice value.
#
# Deliberately `Any` rather than a union of the scalar types we expect. `Mapping`'s key
# type is invariant, so a narrower annotation makes `Mapping[<narrow>, TagChild]` reject
# `dict[int, str]` -- and, surprisingly, `dict[str, str]` as well. `Any` is also honest
# about the runtime contract: any object is accepted and coerced with `str()`.
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

    Without this step, matching on the string form alone would stop honoring a
    numerically equal ``selected``, which used to mark the option checked. Matching on
    raw equality *instead* is not an option either: that is what left the server marking
    an option checked while sending the client a ``"1.0"`` it could never match.
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
    treated as scalars. Any other iterable -- including the ``dict_keys``, ``set``, and
    generator shapes that a caller may build a selection from -- is consumed as a
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
    -- ``json.dumps()`` already serializes a tuple as a JSON array.
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
    Coerce ``selected`` for the radio-button binding, which expects a scalar.

    Sending it a non-empty array is not merely ignored -- ``setValue()`` passes the array
    to ``$escape()``, which calls ``.replace()`` on it and throws, aborting the rest of
    the message handler (so a bundled label update is lost too). A sequence therefore
    collapses to its first element.

    An *empty* sequence is the exception and is preserved as ``[]``: that is the one
    array shape ``setValue()`` special-cases, and it clears the selection. Collapsing it
    to ``None`` would drop ``value`` from the message entirely and leave the previous
    selection in place.
    """
    if x is None:
        return None
    values = _as_raw_list(x)
    if not values:
        return []
    return str(values[0])


class ChoiceSelection:
    """
    Tests whether a choice value is selected: ``choice_value in selection``.

    Comparison is on the string form, since that is the only thing the client can match
    against. Entries that refer to a choice value without stringifying identically are
    handled by :func:`resolve_selected_values` before they get here, not by loosening the
    comparison -- a set lookup keeps this O(1) per choice rather than scanning the
    selection for every option in the group.
    """

    def __init__(self, selected: Any) -> None:
        self._strings = {str(v) for v in _as_raw_list(selected)}

    def __contains__(self, choice: Any) -> bool:
        return str(choice) in self._strings

    def __bool__(self) -> bool:
        return bool(self._strings)
