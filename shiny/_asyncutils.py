import asyncio
import threading
import typing

T = typing.TypeVar("T")


class ThreadsafeAsyncEvent:
    """A version of asyncio.Event that can be set() from another event loop/thread."""

    def __init__(self):
        self._loop = asyncio.get_running_loop()
        self._event = asyncio.Event(loop=self._loop)

    def set(self):
        if asyncio.get_running_loop() is self._loop:
            # Being called from original loop
            self._event.set()
            return

        # Being called from a different loop
        async def _set():
            self._event.set()

        asyncio.run_coroutine_threadsafe(_set(), self._loop)

    async def wait(self) -> typing.Literal[True]:
        self._check_loop("wait")
        return await self._event.wait()

    def clear(self):
        self._check_loop("clear")
        self._event.clear()

    def is_set(self):
        self._check_loop("is_set")
        return self._event.is_set()

    def _check_loop(self, method_name: str):
        if asyncio.get_running_loop() is not self._loop:
            raise RuntimeError(f"{method_name} method was called from the wrong thread")


async def run_elsewhere(
    coro: typing.Awaitable[T], loop: asyncio.AbstractEventLoop
) -> T:
    """Awaitable wrapper for run_coroutine_threadsafe"""

    future = asyncio.run_coroutine_threadsafe(coro, loop)
    evt = ThreadsafeAsyncEvent()

    future.add_done_callback(lambda f: evt.set())

    await evt.wait()
    return future.result()


def create_worker_thread(name: str, daemon: bool = True) -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()

    def _worker_thread():
        nonlocal loop
        asyncio.set_event_loop(loop)
        loop.run_forever()

    threading.Thread(target=_worker_thread, name=name, daemon=daemon).start()

    return loop
