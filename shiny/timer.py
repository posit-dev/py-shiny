import heapq
import dataclasses
import time
from typing import Callable, List, Optional


@dataclasses.dataclass(order=True)
class timerRegistration:
    expiration: float
    callback: Optional[Callable[[], None]] = dataclasses.field(compare=False)


class Timer:
    def __init__(self):
        self._timers: List[timerRegistration] = []

    def register(
        self, delay: float, callback: Callable[[], None]
    ) -> Callable[[], None]:
        return self.register_abs(time.monotonic() + delay, callback)

    def register_abs(
        self, abstime: float, callback: Callable[[], None]
    ) -> Callable[[], None]:
        item = timerRegistration(abstime, callback)
        heapq.heappush(self._timers, item)

        def unregister():
            item.callback = None

        return unregister

    def take_expired(self):
        now = time.monotonic()

        results: List[Callable[[], None]] = []
        while len(self._timers) > 0 and self._timers[0].expiration <= now:
            cb = heapq.heappop(self._timers).callback
            if cb is not None:
                # A callback that was unregistered; just ignore
                results.append(cb)
        return results

    def next_timeout(self, now: Optional[float] = None):
        if len(self._timers) == 0:
            return None

        if now is None:
            now = time.monotonic()
        return max(self._timers[0].expiration - now, 0)
