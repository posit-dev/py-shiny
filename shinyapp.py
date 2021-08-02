from shinysession import ShinySession
import asyncio
import json
import react

class ShinyApp:
    def __init__(self, ui, server) -> None:
        self.ui = ui
        self.server = server

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        server = await asyncio.start_server(self._handle_incoming, '127.0.0.1', 8888)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # Run event loop to listen for events
        async with server:
            await server.serve_forever()


    async def _handle_incoming(self, reader, writer) -> None:
        # When incoming connection arrives, spawn a session
        session = ShinySession(self.server)

        while True:
            line = await reader.readline()
            if not line:
                break

            line = line.decode('latin1').rstrip()

            print("RECV: " + line)

            vals = json.loads(line)
            for (key, val) in vals.items():
                session.input[key] = val

            react.flush()

            for message in session.get_messages():
                message_str = json.dumps(message) + "\n"
                print("SEND: " + message_str, end = "")
                writer.write(message_str.encode('utf-8'))

            session.clear_messages()

        writer.close()
