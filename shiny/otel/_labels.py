"""
OpenTelemetry label generation for reactive spans.

Generates descriptive span names for reactive computations (calcs, effects, outputs)
that include function names, namespaces, and modifiers.
"""

from typing import Any, Callable, Optional

__all__ = ["generate_reactive_label"]


def generate_reactive_label(
    func: Callable[..., Any],
    label_type: str,
    namespace: Optional[str] = None,
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
    namespace
        Optional module namespace prefix (e.g., "my-module")
    modifier
        Optional modifier to include (e.g., "cache", "event")

    Returns
    -------
    str
        A descriptive span label in the format:
        - "reactive myValue" (for simple calc)
        - "reactive cache myValue" (with modifier)
        - "my-module:reactive myValue" (with namespace)
        - "observe <anonymous>" (for lambda function)

    Examples
    --------
    >>> def my_calc():
    ...     return 42
    >>> generate_reactive_label(my_calc, "reactive")
    'reactive my_calc'

    >>> generate_reactive_label(lambda: 42, "observe")
    'observe <anonymous>'

    >>> generate_reactive_label(my_calc, "reactive", namespace="mod", modifier="cache")
    'mod:reactive cache my_calc'
    """
    # Extract function name
    name = getattr(func, "__name__", "<anonymous>")
    if name == "<lambda>":
        name = "<anonymous>"

    # Build label parts
    parts: list[str] = []

    # Add namespace prefix to name if provided
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
