'''
networking
KentStateRobotics Jared Butcher 10/5/2020

Websocket server and client using router module
'''
import logging
import websockets
import asyncio
import threading
import multiprocessing
import enum
import KSRCore.message as message

ROUTER_SLEEP = 0.05
STOP_TIMEOUT = .2

networkingLogger = logging.getLogger("KSRC.Network")
idAssignMessage = message.MessageFactory({})

class NetworkIds(enum.IntEnum):
    LOCAL = 0
    HOST = 1

class Channels(enum.IntEnum):
    NETWORKING = 0
    LOGGING = 1

class Networking(threading.Thread):
    def __init__(self, address):
        super().__init__(name="Networking", daemon=True)
        self._id = None
        self._queue = multiprocessing.Queue()
        self._handlers = {}
        self._handlerLock = threading.Lock()
        self._address = address
        self._eventLoop = None
        self.start()

    @property
    def id(self):
        return self._id

    def send(self, data):
        raise NotImplementedError("Do not use Networking directly")

    def stop(self):
        if self._eventLoop is not None and (self._eventLoop.is_running() or not self._eventLoop.is_closed()):
            def stopLoop():
                self._eventLoop.stop()
            self._eventLoop.call_soon_threadsafe(stopLoop)
        networkingLogger.debug("Stopping networking thread")
        self.join(STOP_TIMEOUT)
        self._queue.close()
        if self.is_alive():
            networkingLogger.warning("Networking thread failed to stop")
            return False
        return True

    def addHandler(self, channel, handler):
        with self._handlerLock:
            self._handlers[channel] = handler

    def removeHandlers(self, channel=None):
        with self._handlerLock:
            if channel is None:
                self._handlers.clear()
            else:
                self._handlers.pop(channel, None)

    def put(self, message):
        self._queue.put(message)

    def run(self):
        self._eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._eventLoop)
        asyncio.run_coroutine_threadsafe(self._runRouter(), self._eventLoop)

    async def _runRouter(self):
        networkingLogger.debug("Starting handler thread")
        while True:
            await asyncio.sleep(ROUTER_SLEEP)
            while not self._queue.empty():
                data = self._queue.get()
                header = message.Message.peekHeader(data)
                handler = None
                if header['destination'] == 0 or header['destination'] == self._id:
                    with self._handlerLock:
                        handler = self._handlers.get(header['channel'])
                        print(self._handlers)
                        print(header['channel'])
                        if handler:
                            handler(data)
                        else:
                            networkingLogger.warning("Unhandled message dropped")
                else:
                    self.send(data)

class Client(Networking):
    def __init__(self, address):
        super().__init__(address)
        self._conn = None

    def send(self, data):
        asyncio.run_coroutine_threadsafe(self._conn.send(data), loop=self._eventLoop)

    def run(self):
        super().run()
        self._server = self._eventLoop.run_until_complete(self._connect())
        self._eventLoop.run_forever()

    def stop(self):
        if self._conn is not None:
            self._conn.close()
        return super().stop()

    async def _connect(self):
        async with websockets.connect(f'ws://{self._address[0]}:{self._address[1]}') as self._conn:
            networkingLogger.debug("Client connected to server")
            while not self._conn.closed:
                try:
                    data = await self._conn.recv()
                except websockets.ConnectionClosedError:
                    break
                #TODO Process received messages
            networkingLogger.warning("Client disconnected from server")

class Server(Networking):
    def __init__(self, port):
        super().__init__(('', port))
        self._id = NetworkIds.HOST.value
        self._clients = {}
        self._clientsLock = threading.Lock()
        self._server = None

    def findUnusedId(self):
        for i in range(0, 253):
            if i + 2 not in self._clients:
                return i + 2
        networkingLogger.error("Out of ids")
        return None

    def send(self, data):
        header = message.Message.peekHeader(data)
        client = self._clients.get(header['destination'])
        if client is not None:
            asyncio.run_coroutine_threadsafe(client.send(data), loop=self._eventLoop)
        else:
            networkingLogger.warning("Client doesn't exist")

    def run(self):
        super().run()
        self._server = self._eventLoop.run_until_complete(websockets.server.serve(self._recNewConn, host=self._address[0], port=self._address[1]))
        self._eventLoop.run_forever()

    def stop(self):
        if self._server is not None:
            self._server.close()
            for client in self._clients.values():
                client.close()
        return super().stop()

    async def _recNewConn(self, conn, url):
        with self._clientsLock:
            id = self.findUnusedId()
            self._clients[id] = conn
        idMessage = idAssignMessage.createMessage()
        idMessage.setHeader(self._id, id, 0x00, 0x00)
        self.send(idMessage.toJson())
        while not conn.closed:
            try:
                print(3)
                data = await conn.recv()
                print("DATA RECIEVD")
            except websockets.ConnectionClosedError:
                break
            header = message.Message.peekHeader(data)
            if header is not None:
                if header['channel'] == Channels.NETWORKING:
                    pass #TODO: assign ids and stuff
                else:
                    self.put(data)
            else:
                networkingLogger.debug("Received malformed network message")
        networkingLogger.debug("Client disconnected from server")
        with self._clientsLock:
            self._clients.pop(id)

