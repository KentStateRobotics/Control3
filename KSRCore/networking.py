'''
networking
KentStateRobotics Jared Butcher 10/5/2020

Websocket server and client using router module
'''
import logging
import websockets
import asyncio
import threading
import message

networkingLogger = logging.getLogger("KSRC.Network")
idAssignMessage = message.MessageFactory('')

class Networking(threading.Thread):
    def __init__(self, address):
        super().__init__(name="Networking", daemon=True)
        self._id = -1
        self._stopEvent = threading.Event()
        self._address = address
        self.start()

    def getId(self):
        return self._id

    def send(self, message):
        raise NotImplementedError("Do not use Networking directly")

    def stop(self):
        self._stopEvent.set()
        networkingLogger.debug("Stopping networking thread")
        self.join(JOIN_TIMEOUT)
        if self.is_alive():
            networkingLogger.warning("Networking thread failed to stop")

    def run(self):
        self._eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._eventLoop)

class Client(Networking):
    def __init__(self):
        pass

class Server(Networking):
    def __init__(self, port):
         super().__init__(('', port))
         self._id = 1
         self._clients = {}
         self._clientsLock = threading.Lock()

    def findUnusedId(self):
        with self._clientsLock:
            for i in range(0, 253):
                if i + 2 not in self._clients:
                    return i + 2
        networkingLogger.error("Out of ids")
        return -1

    def run():
        super().run()
        self._server = self._eventLoop.run_until_complete(websockets.server.serve(self._recNewConn, host=self._address[0], port=self._address[1], loop=self._eventLoop))
        self.loop.run_forever()

    async def _recNewConn(self, conn, url):
        id = self.findUnusedId()
        self._clients[id] = conn
        idMessage = idAssignMessage.createMessage()
        idMessage.setHeader(self._id, id, 0x00, 0x00)
        self.send(idMessage.toJson())
        while not self._stopEvent.is_set() and not conn.closed():
            try:
                data = await conn.recv()
            except websockets.ConnectionClosedError:
                break
        self._clients.pop(id)

