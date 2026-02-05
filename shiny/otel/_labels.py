"""
OpenTelemetry label generation for reactive spans.

Generates descriptive span names for reactive computations (calcs, effects, outputs)
that include function names, namespaces, and modifiers.
"""

from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    from ..session import Session

__all__ = ["generate_reactive_label"]


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
