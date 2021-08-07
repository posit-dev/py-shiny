from typing import Union, Callable, Any
from shinysession import ShinySession, Outputs
from reactives import ReactiveValues
import react
from iomanager import IOManager, IOHandler, FastAPIIOManager, TCPIOManager



class ShinyApp:
    def __init__(self, ui: Any, server: Callable[[ReactiveValues, Outputs], None]) -> None:
        self.ui: Any = ui
        self.server: Callable[[ReactiveValues, Outputs], None] = server
        self._sessions: dict[int, ShinySession] = {}
        self._last_session_id: int = 0    # Counter for generating session IDs

        self._sessions_needing_flush: dict[int, ShinySession] = {}

    def create_session(self, iohandler: IOHandler) -> ShinySession:
        self._last_session_id += 1
        id = self._last_session_id
        session = ShinySession(self, id, iohandler)
        self._sessions[id] = session
        return session

    def remove_session(self, session: Union[ShinySession, int]) -> None:
        if (isinstance(session, ShinySession)):
            session = session.id

        print(f"remove_session: {session}")
        del self._sessions[session]

    def run(self, iotype: str = "websocket") -> None:
        if (iotype == "websocket"):
            self._iomanager: IOManager = FastAPIIOManager(self._on_connect_cb)
        elif (iotype == "tcp"):
            self._iomanager: IOManager = TCPIOManager(self._on_connect_cb)
        else:
            raise ValueError(f"Unknown iotype {iotype}")

        self._iomanager.run()

    async def _on_connect_cb(self, iohandler: IOHandler) -> None:
        """Callback passed to the IOManager which is invoked when a new
        connection is established."""
        session = self.create_session(iohandler)
        await session.serve()

    def request_flush(self, session: ShinySession) -> None:
        # TODO: Until we have reactive domains, because we can't yet keep track
        # of which sessions need a flush.
        pass
        # self._sessions_needing_flush[session.id] = session

    async def flush_pending_sessions(self) -> None:
        react.flush()

        # TODO: Until we have reactive domains, flush all sessions (because we
        # can't yet keep track of which ones need a flush)
        for id, session in self._sessions.items():
            await session.flush()
        # for id, session in self._sessions_needing_flush.items():
        #     await session.flush()
        #     del self._sessions_needing_flush[id]
