import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Generator

from ..._docstring import no_example

__all__ = ("expect_to_change",)


@no_example()
@contextmanager
def expect_to_change(
    func: Callable[[], Any], timeout_secs: float = 10
) -> Generator[None, None, None]:
    """
    Context manager that yields when the value returned by func() changes.

    Use this around code that has a side-effect of changing some state asynchronously
    (such as all browser actions), to prevent moving onto the next step of the test
    until this one has actually taken effect.

    Parameters
    ----------
    func
        A function that returns a value. The value returned by this function is
        compared to the value returned by subsequent calls to this function.
    timeout_secs
        How long to wait for the value to change before raising TimeoutError.

    Raises
    ------
    TimeoutError
        If the value does not change within timeout_secs.

    Example
    -------

        with expect_to_change(lambda: page.locator("#name").value()):
            page.keyboard.send_keys("hello")

    """

    original_value = func()
    yield

    @retry_with_timeout(timeout_secs)
    def wait_for_change():
        if func() == original_value:
            raise AssertionError("Value did not change")

    wait_for_change()


@no_example()
def retry_with_timeout(timeout: float = 30):
    """
    Decorator that retries a function until 1) it succeeds, 2) fails with a
    non-assertion error, or 3) repeatedly fails with an AssertionError for longer than
    the timeout. If the timeout elapses, the last AssertionError is raised.

    Parameters
    ----------
    timeout
        How long to wait for the function to succeed before raising the last
        AssertionError.

    Returns
    -------
    A decorator that can be applied to a function.

    Example
    -------

        @retry_with_timeout(30)
        def try_to_find_element():
            if not page.locator("#name").exists():
                raise AssertionError("Element not found")

        try_to_find_element()
    """

    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        @functools.wraps(func)
        def wrapper() -> None:
            start = time.time()
            while True:
                try:
                    return func()
                except AssertionError as e:
                    if time.time() - start > timeout:
                        raise e
                    time.sleep(0.1)

        return wrapper

    return decorator
