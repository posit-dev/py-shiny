from typing import Union
from shinysession import ShinySession
import react
from iomanager import IOManager, IOHandle, FastAPIIOManager, TCPIOManager



class ShinyApp:
    def __init__(self, ui, server: callable) -> None:
        self.ui = ui
        self.server: callable = server
        self._sessions: dict[int, ShinySession] = {}
        self._last_session_id: int = 0    # Counter for generating session IDs

        self._sessions_needing_flush: dict[int, ShinySession] = {}

    def create_session(self, iohandle: IOHandle) -> ShinySession:
        self._last_session_id += 1
        id = self._last_session_id
        session = ShinySession(self, id, iohandle)
        self._sessions[id] = session
        return session

    def remove_session(self, session: Union[ShinySession, int]) -> None:
        if (isinstance(session, ShinySession)):
            session = session.id

        print(f"remove_session: {session}")
        del self._sessions[session]

    def run(self, iotype = "websocket") -> None:
        if (iotype == "websocket"):
            self._iomanager: IOManager = FastAPIIOManager(self)
        elif (iotype == "tcp"):
            self._iomanager: IOManager = TCPIOManager(self)
        else:
            raise ValueError(f"Unknown iotype {iotype}")

        self._iomanager.run()

    def request_flush(self, session) -> None:
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
