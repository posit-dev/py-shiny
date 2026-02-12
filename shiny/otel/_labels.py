"""
OpenTelemetry label generation for reactive spans.

Generates descriptive span names for reactive computations (calcs, effects, outputs)
that include function names, namespaces, and modifiers.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from ..session import Session

__all__ = [
    "generate_reactive_label",
    "get_otel_label_modifier",
    "set_otel_label_modifier",
]

# Attribute name used to store modifiers on function objects
_MODIFIER_ATTR = "_shiny_otel_label_modifier"


def generate_reactive_label(
    func: Callable[..., Any],
    label_type: str,
    session: "Session | None" = None,
    modifier: Optional[str] = None,
) -> str:
    """
    Generate a descriptive label for a reactive computation span.

    Parameters
    ----------
    func
        The reactive function to generate a label for.
    label_type
        The type of reactive computation. Common values:
        - "reactive" for Calc
        - "observe" for Effect
        - "output" for Output rendering
    session
        Optional session to extract namespace from. If provided and the session
        has a namespace, it will be included in the label.
    modifier
        Optional modifier to include (e.g., "cache", "event")

    Returns
    -------
    str
        A descriptive span label in the format:
        - "reactive myValue" (for simple calc)
        - "reactive cache myValue" (with modifier)
        - "reactive mod:myValue" (with namespace)
        - "reactive cache mod:myValue" (with namespace and modifier)
        - "observe <anonymous>" (for lambda function)

    Examples
    --------
    >>> def my_calc():
    ...     return 42
    >>> generate_reactive_label(my_calc, "reactive")
    'reactive my_calc'

    >>> generate_reactive_label(lambda: 42, "observe")
    'observe <anonymous>'

    >>> generate_reactive_label(my_calc, "reactive", session=mock_session, modifier="cache")
    'reactive cache mod:my_calc'
    """
    # Extract function name
    name = getattr(func, "__name__", "<anonymous>")
    if name == "<lambda>":
        name = "<anonymous>"

    # Build label parts
    parts: list[str] = []

    # Extract namespace from session if provided
    namespace: str | None = None
    if session is not None:
        # session.ns is a ResolvedId (subclass of str)
        # It will be an empty string ("") for Root namespace
        ns_str = str(session.ns)
        if ns_str:  # Only use non-empty namespaces
            namespace = ns_str

    # Add namespace prefix to name if present
    if namespace:
        name = f"{namespace}:{name}"

    # Add label type
    parts.append(label_type)

    # Add modifier if provided
    if modifier:
        parts.append(modifier)

    # Add function name
    parts.append(name)

    return " ".join(parts)


def get_otel_label_modifier(func: Callable[..., Any]) -> Optional[str]:
    """
    Get the OTel label modifier from a function.

    Retrieves the modifier string that has been set on a function object,
    typically by decorators like `@reactive.event()`.

    Parameters
    ----------
    func
        The function to retrieve the modifier from.

    Returns
    -------
    str | None
        The modifier string if set (e.g., "event", "event cache"), or None if
        no modifier has been set.

    Examples
    --------
    >>> def my_func():
    ...     return 42
    >>> get_otel_label_modifier(my_func)
    None

    >>> @reactive.event(input.x)
    ... def my_event_func():
    ...     return 42
    >>> get_otel_label_modifier(my_event_func)
    'event'
    """
    return getattr(func, _MODIFIER_ATTR, None)


def set_otel_label_modifier(
    func: Callable[..., Any],
    modifier: str,
    *,
    mode: str = "prepend",
) -> None:
    """
    Set the OTel label modifier on a function.

    Stores a modifier string on a function object that will be used when
    generating OTel span labels for reactive computations.

    Parameters
    ----------
    func
        The function to set the modifier on.
    modifier
        The modifier string to set (e.g., "event", "cache").
    mode
        How to combine with existing modifiers:
        - "prepend" (default): Add before existing modifiers
        - "append": Add after existing modifiers
        - "replace": Replace all existing modifiers

    Examples
    --------
    >>> def my_func():
    ...     return 42
    >>> set_otel_label_modifier(my_func, "event")
    >>> get_otel_label_modifier(my_func)
    'event'

    >>> set_otel_label_modifier(my_func, "cache")
    >>> get_otel_label_modifier(my_func)  # mode="prepend" by default
    'cache event'

    >>> set_otel_label_modifier(my_func, "debounce", mode="append")
    >>> get_otel_label_modifier(my_func)
    'cache event debounce'

    >>> set_otel_label_modifier(my_func, "throttle", mode="replace")
    >>> get_otel_label_modifier(my_func)
    'throttle'

    Note
    ----
    This function modifies the function object in-place by setting an attribute
    on its `__dict__`. The attribute name used is stored in `_MODIFIER_ATTR`.
    """
    existing = getattr(func, _MODIFIER_ATTR, None)

    if mode == "replace" or existing is None:
        # Replace mode or no existing modifier - just set it
        new_modifier = modifier
    elif mode == "prepend":
        # Prepend: new modifier comes first
        new_modifier = f"{modifier} {existing}"
    elif mode == "append":
        # Append: new modifier comes last
        new_modifier = f"{existing} {modifier}"
    else:
        raise ValueError(
            f"Invalid mode: {mode!r}. Must be 'prepend', 'append', or 'replace'."
        )

    setattr(func, _MODIFIER_ATTR, new_modifier)
