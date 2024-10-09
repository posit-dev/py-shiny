# TODO-barret; Schedule meeting with Joe when done

import inspect

# from types import UnboundMethodType
# import types
from functools import wraps
from typing import Any, Callable, TypeVar
from weakref import WeakKeyDictionary

from ... import reactive

R = TypeVar("R")
S = TypeVar("S")

# TODO-future: Can we do this for effect?
# reactive_value_method
#     @reactive.value
#     def __some_effect(self):
#         # Should be possible as it doesn't need to run on init, only on demand!
#         ...
# reactive_effect_method
#     @reactive.effect
#     def __some_effect(self):
#         # Thinking it is impossible to do!
#         # There is no way to get the `session` within the init method
#         # We should throw an error if we find this situation
#         ...


def is_class_method(fn: Callable[..., Any]) -> bool:
    """
    Determine if a function is a class method.

    This function checks if a function is a class method by checking if the function's
    `__qualname__` ends with a non-`<locals>` value before the function name.

    Parameters
    ----------
    fn
        The function to check.

    Returns
    -------
    :
        True if the function is a class method, False otherwise.
    """
    # if not inspect.isfunction(fn) and not inspect.ismethod(fn):
    if not inspect.isfunction(fn):
        return False

    # Check if the function's __qualname__ contains a class name
    if "." not in fn.__qualname__:
        # If no `.` in the qualname, it is not a class method
        return False

    # `__qualname__` is the fully qualified name of the function
    # It contains the class name if the function is a class method
    # If the qualname has `<locals>` just before the final `__name__` value, it is a nested function.
    # (Nested Class definitions are ok. Nested function definitions are not)
    scope_name, fn_name = fn.__qualname__.rsplit(".", 1)

    # If we find a nested function, it is not a class method
    if scope_name.endswith("<locals>"):
        return False

    if fn_name != fn.__name__:
        # If the final value of the qualname should always be the function name
        return False

    # Must be a class method!
    return True


def reactive_calc_method(fn: Callable[[S], R]) -> Callable[[S], R]:

    # Can not use `inspect.ismethod` as it will return False for class definition methods,
    # but True for class instance methods. Ex: Barret.get_name vs barret.get_name

    if not (inspect.isfunction(fn) and is_class_method(fn)):
        raise TypeError("reactive_calc_method should only be used on class methods")

    calc_cache: WeakKeyDictionary[S, reactive.Calc_[R]] = WeakKeyDictionary()

    @wraps(fn)
    def _(self: S) -> R:

        if self not in calc_cache:

            # # While the code below is more concise, functools.partial does not create
            # # `.__docs__` and `.__name__` attributes
            # # https://docs.python.org/3/library/functools.html#partial-objects
            # calc_cache[self] = reactive.calc(functools.partial(fn, self))

            @reactive.calc
            @wraps(fn)
            def calc_fn():
                return fn(self)

            # Set calc method
            calc_cache[self] = calc_fn

            # Store the reactive calc function on self's fn, so that `calc_fn` does not
            # get garbage collected. Before these lines, it is isolated under a weak
            # key. After these lines, it is stored on self's `__dict__` and should not
            # be garbage collected until `self` is garbage collected.
            if not hasattr(self.__dict__, "_reactive_calc_method"):
                self.__dict__["_reactive_calc_method"] = {}
            self_reactive_calc_cache: dict[str, reactive.Calc_[R]] = self.__dict__[
                "_reactive_calc_method"
            ]
            if hasattr(self_reactive_calc_cache, fn.__name__):
                raise AttributeError(
                    f"Reactive calc method `{fn.__name__}` has already be cached on self: {self}"
                )
            self_reactive_calc_cache[fn.__name__] = calc_fn

        return calc_cache[self]()

    return _
