'''
KentStateRobotics Jared Butcher 10/5/2020

Interprocess router packaged in either a websocket client or server. 
'''
import logging
from typing import Union, Callable, Optional
import websockets
import asyncio
import threading
import multiprocessing
import enum
import copy
import KSRCore.message as message
import KSRCore.logging
import KSRCore.discovery as discovery
import KSRCore.config as config

DEFAULT_PORT = 4242
ROUTER_SLEEP = 0.05
STOP_TIMEOUT = .2

networkingLogger = logging.getLogger(KSRCore.logging.BASE_LOGGER + '.Network')
connectToMessage = message.MessageFactory({'port': 'i', 'addresss': 'blob'})
logMessage = message.MessageFactory({'level': 'i', 'name': '32p', 'message': 'blob'})

class NetworkIds(enum.IntEnum):
    '''Enum of reserved addresses'''
    LOCAL = 0
    HOST = 1

class Channels(enum.IntEnum):
    '''Enum of general channels'''
    NETWORKING = 0

class NetworkingTypes(enum.IntEnum):
    '''Enum of message types for the networking channel'''
    ID_ASSIGN = 0
    CONNECT_TO = 1
    LOG = 2

class Networking(threading.Thread):
    '''Base for networking server and client. Serves as interprocess router
        Should not be instantiated directly, use Server or Client. 
        Only one is needed per machine
        Processes need to register a handler for receiving messages before forking
    '''
    def __init__(self, address, retryTimeout: Optional[int] = 1):
        '''Instanciation tarts queue, rotuer, and thread
        '''
        super().__init__(name="Networking", daemon=True)
        self._id = None
        self._queue = multiprocessing.Queue()
        self._handlers = {}
        self._handlerLock = threading.Lock()
        self._address = address
        self._eventLoop = None
        self._discovery = None
        self._retryCounter = 0
        self._retryTimeout = retryTimeout
        self.addHandler(Channels.NETWORKING.value, self.handleNetworkChannel)
        self.start()

    @property
    def id(self) -> int:
        '''Returns Id of this router. 
            Servers will always be 1.
            Clients cannot send messages until an id is received from the server.
        '''
        return self._id

    @property
    def queue(self) -> 'multiprocessing.Queue':
        return self._queue

    def send(self, data: Union[bytes, str]):
        '''Send data over network to destintation of Message

            `data` is a packaged `KSRCore.message.Message`
        '''
        raise NotImplementedError("Do not use Networking directly")

    def stop(self) -> bool:
        '''Stop the router, and router queue along with any threads.
            Returns if all threads sucessfully closed
        '''
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

    def addHandler(self, channel: int, handler: Callable[['KSRCore.message.Message', Union[bytes, str]], None]):
        '''Add a handler to handle messages on given channel

            `channel` 0-255 channel to receive on

            `handler` callback receiving a packaged `KSRCore.message.Message`
        '''
        with self._handlerLock:
            self._handlers[channel] = handler

    def removeHandlers(self, channel: int = None):
        '''Remove handler(s). If channel is not given remove all handlers
            `channel` (int, 0-255, optional): channel to remove
        '''
        with self._handlerLock:
            if channel is None:
                self._handlers.clear()
            else:
                self._handlers.pop(channel, None)

    def put(self, data: Union[bytes, str]):
        '''Put a packaged `KSRCore.message.Message` into the routing system
        '''
        self._queue.put(data)

    def run(self):
        self._eventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._eventLoop)
        self._eventLoop.create_task(self._runRouter())

    def handleNetworkChannel(self, header: 'KSRCore.message.Message', message: Union[bytes, str]):
        '''Called by router on receiving a networking message, do not call directly'''
        pass

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
                            handler(header, data)
                        else:
                            networkingLogger.warning("Unhandled message dropped")
                else:
                    if header['source'] == 0:
                        message.Message.setSource(data, self.id)
                    if not self.send(data):
                        readd.append(data)
            [self._queue.put(data) for data in readd]

class Client(Networking):
    '''Connects to a server and serves as interprocess router.
        Processes need to register a handler for receiving messages before forking
        Also attaches a remote logger to log back to the server
    '''
    def __init__(self, address: (str, int), retryTimeout=1):
        '''`address` is a pair of host address and port number
        '''
        super().__init__(address, retryTimeout)
        self._conn = None
        self._discovery = discovery.Discovery(address[1] + 1)
        self._tryReconnect = True
        self._remoteLogHandler = None

    def send(self, data):
        if self._retryCounter > self._retryTimeout and (not self._conn or self._conn.closed):
            networkingLogger.error("Message send timeout expired")
            return True
        elif self._conn and not self._conn.closed:
            asyncio.run_coroutine_threadsafe(self._conn.send(data), loop=self._eventLoop)
            return True
        else:
            self._retryCounter += ROUTER_SLEEP
            return False

    def run(self):
        super().run()
        self._eventLoop.create_task(self._connect())
        try:
            self._eventLoop.run_forever()
        finally:
            self._eventLoop.close()

    def stop(self):
        self._tryReconnect = False
        if self._conn is not None:
            asyncio.run_coroutine_threadsafe(self._conn.close(), loop=self._eventLoop)
        return super().stop()

    def handleNetworkChannel(self, header, message: Union[bytes, str]):
        if header['type'] == NetworkingTypes.CONNECT_TO.value:
            message = connectToMessage.loads(message)
            self._address = (str(message['addresss']), message['port'])
            if self._conn and not self._conn.closed:
                asyncio.run_coroutine_threadsafe(self._connect(), loop=self._eventLoop)
        elif header['type'] == NetworkingTypes.LOG.value:
            message = logMessage.loads(message)
            logger = logging.getLogger(message['name'].decode('utf-8'))
            logger.log(message['level'], message['message'].decode('utf-8'))

    def isConnected(self) -> bool:
        return not self._conn.closed if self._conn else False

    async def _connect(self):
        if self._conn and not self.conn.closed:
            await self._conn.close()
        if not self._address[0]:
            self._address = (self._discovery.find(config.DISCOVERY_ID, 5), self._address[1])
        if self._address[0]:
            async with websockets.connect(f'ws://{self._address[0]}:{self._address[1]}') as self._conn:
                self._retryCounter = 0
                KSRCore.logging.addRemoteHandler(self.queue)
                networkingLogger.debug("Client connected to server")
                while not self._conn.closed:
                    try:
                        data = await self._conn.recv()
                    except websockets.ConnectionClosedError:
                        break
                    header = message.Message.peekHeader(data)
                    if header:
                        if header['channel'] == Channels.NETWORKING.value and header['type'] == NetworkingTypes.ID_ASSIGN.value:
                            self._id = header['destination']
                        else:
                            self.put(data)
                    else:
                        networkingLogger.warning("Received malformed message")
                networkingLogger.warning("Client disconnected from server")
            if self._tryReconnect:
                if self._remoteLogHandler:
                    logging.getLogger().removeHandler(self._remoteLogHandler)
                asyncio.run_coroutine_threadsafe(self._connect(), loop=self._eventLoop)
        else:
            networkingLogger.error(f'Could not connect to address {self._address[0]} or find using discovery')

class Server(Networking):
    '''Host a server for clients and serves as interprocess and intermachines router.
        Processes need to register a handler for receiving messages before forking
    '''
    def __init__(self, port: int, retryTimeout=1):
        '''Bind to `port` and start hosting the server and run the router
        '''
        super().__init__(('', port),retryTimeout)
        self._id = NetworkIds.HOST.value
        self._clients = {}
        self._clientsLock = threading.Lock()
        self._discovery = discovery.Discovery(port + 1)
        self._server = None

    def findUnusedId(self) -> int:
        '''Return an unused id from 0-255
        '''
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
        return True

    def run(self):
        super().run()
        self._eventLoop.create_task(self._discovery.echoAddress(config.DISCOVERY_ID, self._eventLoop))
        self._server = self._eventLoop.run_until_complete(websockets.server.serve(self._recNewConn, host=self._address[0], port=self._address[1]))
        try:
            self._eventLoop.run_forever()
        finally:
            self._eventLoop.close()

    def stop(self):
        if self._server is not None:
            self._server.close()
            for client in self._clients.values():
                client.close()
        return super().stop()

    def handleNetworkChannel(self, header, message: Union[bytes, str]):
        if header['type'] == NetworkingTypes.LOG.value:
            message = logMessage.loads(message)
            logger = logging.getLogger(message['name'].decode('utf-8'))
            logger.log(message['level'], message['message'].decode('utf-8'))

    async def _recNewConn(self, conn, url):
        with self._clientsLock:
            id = self.findUnusedId()
            self._clients[id] = conn
        idMessage = message.justHeaderMessage.createMessage()
        idMessage.setHeader(self._id, id, 0x00, NetworkingTypes.ID_ASSIGN.value)
        self.send(idMessage.toJson())
        while not conn.closed:
            try:
                data = await conn.recv()
            except websockets.ConnectionClosed:
                break
            header = message.Message.peekHeader(data)
            if header is not None:
                self.put(data)
            else:
                networkingLogger.debug("Received malformed network message")
        networkingLogger.debug("Client disconnected from server")
        with self._clientsLock:
            self._clients.pop(id)
