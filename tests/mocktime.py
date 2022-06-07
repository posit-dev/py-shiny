import asyncio
import contextlib
import typing
import unittest.mock


class MockTime:
    """Patches time.monotonic() and asyncio.sleep(), replacing actual time with
    simulated time. The intention is to allow time-based code to be unit tested faster
    than realtime.

    Note that this class doesn't currently patch other asyncio time-based functions like
    wait_for(), wait(), as_completed() (although I think we certainly could--we just
    don't need them at this time).
    """

    def __init__(self, now: float = 0):
        self._time = now
        # The tuple elements are 1) time to wake, 2) tiebreaking int, 3) event to be
        # signaled upon wake. The tiebreaking int is necessary to make sorting possible
        # when two sleepers have the same time to wake, as asyncio.Event instances
        # cannot be compared to each other.
        self._sleepers: typing.List[typing.Tuple[float, int, asyncio.Event]] = []
        self._is_advancing = False
        self._i = 0

    @contextlib.contextmanager
    def __call__(self):
        with unittest.mock.patch("time.monotonic", new=self._monotonic):
            with unittest.mock.patch("asyncio.sleep", new=self._sleep):
                yield

    def _monotonic(self):
        return self._time

    async def advance_time(self, secs: float):
        if self._is_advancing:
            raise RuntimeError("MockTime.advance was called reentrantly")

        self._is_advancing = True
        try:
            if secs < 0:
                raise ValueError("MockTime cannot move backwards in time")
            end_time = self._time + secs

            await yield_event_loop()

            # It's OK for self._sleepers to be mutated as we go
            while len(self._sleepers) > 0 and self._sleepers[0][0] <= end_time:
                self._time = self._sleepers[0][0]
                self._sleepers.pop(0)[2].set()

                # Give just-awakened task a chance to run.
                await yield_event_loop()
            self._time = end_time

            await yield_event_loop()

        finally:
            self._is_advancing = False

    async def _sleep(self, delay: float) -> None:
        delay = max(0, delay)
        target = self._time + delay
        wake = asyncio.Event()
        self._sleepers.append((target, self._i, wake))
        self._i += 1
        # Oldest first
        self._sleepers.sort()
        await wake.wait()


async def yield_event_loop():
    # Ordinarily we'd just call asyncio.sleep(0), but we've mocked it, so we have to do
    # something lower-level.

    f: asyncio.Future[None] = asyncio.Future()

    def done():
        f.set_result(None)

    asyncio.get_event_loop().call_soon(done)
    await f
