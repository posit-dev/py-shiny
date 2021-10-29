from typing import Optional, Dict, Any
from warnings import warn
from .utils import run_coro_sync, rand_hex
from .shinysession import ShinySession, _require_active_session


class Progress:
    _style = "notification"

    def __init__(
        self, min: int = 0, max: int = 1, session: Optional[ShinySession] = None
    ):
        self.min = min
        self.max = max
        self.value = None
        self._id = rand_hex(8)
        self._closed = False
        self._session = _require_active_session(session, "Progress")

        msg = {"id": self._id, "style": self._style}
        self._send_progress("open", msg)

    def set(
        self,
        value: float,
        message: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        if self._closed:
            warn("Attempting to set progress, but progress already closed.")
            return None

        self.value = value
        if value:
            # Normalize value to number between 0 and 1
            value = min(1, max(0, (value - self.min) / (self.max - self.min)))

        msg = {
            "id": self._id,
            "message": message,
            "detail": detail,
            "value": value,
            "style": self._style,
        }

        self._send_progress("update", {k: v for k, v in msg.items() if v is not None})

    def inc(
        self,
        amount: float = 0.1,
        message: Optional[str] = None,
        detail: Optional[str] = None,
    ):
        if self.value is None:
            self.value = self.min

        value = min(self.value + amount, self.max)
        self.set(value, message, detail)

    def close(self):
        if self._closed:
            warn("Attempting to close progress, but progress already closed.")
            return None

        self._send_progress("close", {"id": self._id, "style": self._style})
        self._closed = True

    def _send_progress(self, type: str, message: Dict[str, Any]):
        return run_coro_sync(
            self._session.send_message({"progress": {"type": type, "message": message}})
        )
