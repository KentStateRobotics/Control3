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

DEFAULT_PORT = 4242
ROUTER_SLEEP = 0.05
STOP_TIMEOUT = .2

networkingLogger = logging.getLogger("KSRC.Network")
idAssignMessage = message.MessageFactory({})

class NetworkIds(enum.IntEnum):
    '''Reserved addresses'''
    LOCAL = 0
    HOST = 1

class Channels(enum.IntEnum):
    '''General channels'''
    NETWORKING = 0
    LOGGING = 1

class NetworkingTypes(enum.IntEnum):
    '''Message types for the networking channel'''
    ID_ASSIGN = 0

class Networking(threading.Thread):
    '''Base for networking server and client. Serves as interprocess router
    Should not be instantiated directly, use Server or Client. 
    Only one is needed per machine
    Processes need to register a handler for receiving messages before forking
    '''
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
        '''Id of this router. 
        Servers will always be 1.
        Clients cannot send messages until an id is received from the server.
        '''
        return self._id

    def send(self, data):
        raise NotImplementedError("Do not use Networking directly")

    def stop(self):
        async def stopLoop(tasks):
            await asyncio.gather(*tasks, return_exceptions=True)
            self._eventLoop.stop()
        with self._handlerLock:
            if self._eventLoop is not None and (self._eventLoop.is_running() or not self._eventLoop.is_closed()):
                tasks = asyncio.all_tasks(loop=self._eventLoop)
                [task.cancel() for task in tasks]
                self._eventLoop.create_task(stopLoop(tasks))
            networkingLogger.debug("Stopping networking thread")
            self.join(STOP_TIMEOUT)
        self._queue.close()
        if self.is_alive():
            networkingLogger.warning("Networking thread failed to stop")
            return False
        return True

    def addHandler(self, channel, handler):
        '''Add a handler to handle messages on given channel
        Args:
            channel (int, 0-255): channel to receive on
            handler (function(str/bytes)): callback receiving a bytes or string representaion of a Message
        '''
        with self._handlerLock:
            self._handlers[channel] = handler

    def removeHandlers(self, channel=None):
        '''Remove handler(s). If channel is not given remove all handlers
        '''
        with self._handlerLock:
            if channel is None:
                self._handlers.clear()
            else:
                self._handlers.pop(channel, None)

    def put(self, data):
        '''Put the bytes or json representaion of a Message into the routing queue
        Args:
            data (bytes | str): bytes or json representaion of a Message
        '''
        self._queue.put(data)

    def run(self):
        self._eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._eventLoop)
        self._eventLoop.create_task(self._runRouter())

    async def _runRouter(self):
        networkingLogger.debug("Starting handler thread")
        while True:
            await asyncio.sleep(ROUTER_SLEEP)
            readd = []
            while not self._queue.empty():
                data = self._queue.get()
                header = message.Message.peekHeader(data)
                handler = None
                if header['destination'] == 0 or header['destination'] == self._id:
                    with self._handlerLock:
                        handler = self._handlers.get(header['channel'])
                        if handler:
                            handler(data)
                        else:
                            networkingLogger.warning("Unhandled message dropped")
                else:
                    if not self.send(data):
                        readd.append(data)
            [self._queue.put(data) for data in readd]

class Client(Networking):
    '''Connects to a server and serves as interprocess router.
        Processes need to register a handler for receiving messages before forking
    Args:
        address ((str, int)): pair of address and port to connect to
    '''
    def __init__(self, address):
        super().__init__(address)
        self._conn = None
        self._tryReconnect = True

    def send(self, data):
        '''Send data over network to destintation of Message
        Args:
            data (bytes | str): bytes or json representation of a Message
        '''
        if self._conn and not self._conn.closed:
            asyncio.run_coroutine_threadsafe(self._conn.send(data), loop=self._eventLoop)
            return True
        else:
            return False

    def run(self):
        super().run()
        self._eventLoop.create_task(self._connect())
        try:
            self._eventLoop.run_forever()
        finally:
            self._eventLoop.close()

    def stop(self):
        '''Stop the client, router, and router queue along with any threads.
        Returns if all threads sucessfully closed
        '''
        self._tryReconnect = False
        if self._conn is not None:
            asyncio.run_coroutine_threadsafe(self._conn.close(), loop=self._eventLoop)
        return super().stop()

    async def _connect(self):
        async with websockets.connect(f'ws://{self._address[0]}:{self._address[1]}') as self._conn:
            networkingLogger.debug("Client connected to server")
            while not self._conn.closed:
                try:
                    data = await self._conn.recv()
                except websockets.ConnectionClosedError:
                    break
                header = message.Message.peekHeader(data)
                if header:
                    if header['channel'] == Channels.NETWORKING:
                        if header['type'] == NetworkingTypes.ID_ASSIGN:
                            self._id = header['destination']
                    else:
                        self.put(data)
                else:
                    networkingLogger.warning("Received malformed message")
            networkingLogger.warning("Client disconnected from server")
        if self._tryReconnect:
            asyncio.run_coroutine_threadsafe(self._connect(), loop=self._eventLoop)

class Server(Networking):
    '''Host a server for clients and serves as interprocess and intermachines router.
        Processes need to register a handler for receiving messages before forking
    Args:
        port (int): port to bind to
    '''
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
        '''Send data over network to destintation of Message
        Args:
            data (bytes | str): bytes or json representation of a Message
        '''
        header = message.Message.peekHeader(data)
        client = self._clients.get(header['destination'])
        if client is not None:
            asyncio.run_coroutine_threadsafe(client.send(data), loop=self._eventLoop)
        else:
            networkingLogger.warning("Client doesn't exist")

    def run(self):
        super().run()
        self._server = self._eventLoop.run_until_complete(websockets.server.serve(self._recNewConn, host=self._address[0], port=self._address[1]))
        try:
            self._eventLoop.run_forever()
        finally:
            self._eventLoop.close()

    def stop(self):
        '''Stop the server, router, and router queue along with any threads.
        Returns if all threads sucessfully closed
        '''
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
        idMessage.setHeader(self._id, id, 0x00, NetworkingTypes.ID_ASSIGN)
        self.send(idMessage.toJson())
        while not conn.closed:
            try:
                data = await conn.recv()
            except websockets.ConnectionClosed:
                break
            header = message.Message.peekHeader(data)
            if header is not None:
                if header['channel'] == Channels.NETWORKING:
                    pass #TODO stuff here
                else:
                    self.put(data)
            else:
                networkingLogger.debug("Received malformed network message")
        networkingLogger.debug("Client disconnected from server")
        with self._clientsLock:
            self._clients.pop(id)

