import websockets
import threading
import asyncio
from .networkCore import NetworkCore
from .subscriber import Subscriber
from .message import Message
from . import messages

class Server(NetworkCore):
    '''Starts the network server. Interface with it as a NetworkCore object
    '''
    def __init__(self, name, port):
        super().__init__(name, port)
        self.clients = []
        self.alive = True
        self.subcriberRegistrationSub = self.addSubscriber('', Subscriber.REGISTRATION_TOPIC, Message.MessageType.publisher.value, messages.SubscriberMsg, self._recSubRegister)
        self.serverThread = Server.Thread(self)
        self.serverThread.start()

    def send(self, header, message):
        '''Sends message to all clients with subscribers to it
        '''
        for client in self.clients:
            for sub in client.subscribers:
                if Subscriber.registrationMatch(sub, header):
                    client.send(message)
                    break

    def close(self):
        '''Shutdown server, gracefuly?
        '''
        #self.serverThread.loop.call_soon_threadsafe(self.serverThread.close)
        self.alive = False
        print("Server is Closing")
        if not self.serverThread.loop is None:
            asyncio.run_coroutine_threadsafe(self.serverThread.close(), self.serverThread.loop)
        self.serverThread.join()

    def addSubscriber(self, source, topic, messageType, message, callback):
        '''Please use this to create subscribers
        '''
        sub = Subscriber(source, topic, messageType, message, callback)
        self.subscribers.append(sub)
        return sub

    def removeSubscriber(self, subscriber):
        self.subscribers.remove(subscriber)

    def isConnected(self):
        '''We are proably safe to assume we are connected to the server
        '''
        return True

    def _recSubRegister(self, message):
        for client in self.clients:
            if message['header']['source'] == client.name:
                if message['remove']:
                    for sub in client.subscribers:
                        if Subscriber.registrationMatch(message, sub):
                            client.subscribers.remove(sub)
                else:
                    client.subscribers.append(message)
                break

    class Thread(threading.Thread):
        def __init__(self, server):
            self.loop = None
            self.server = server
            threading.Thread.__init__(self)
            
        def run(self):
            if not self.server.onConnect is None:
                self.server.onConnect()
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            print("Starting Server")
            self.wsServer = self.loop.run_until_complete(websockets.server.serve(self._recNewConn, host='', port=self.server.port, loop=self.loop))
            self.loop.run_forever()

        async def _recNewConn(self, conn, url):
            print("Received new Connection Request")
            client = Server.Client(self.server, conn)
            self.server.clients.append(client)
            await client.read()

        async def close(self):
            self.wsServer.close()
            await self.wsServer.wait_closed()
            self.loop.stop()
            
    class Client():
        def __init__(self, server, connection):
            self.subscribers = []
            self.server = server
            self.connection = connection
            self.name = ''

        async def read(self):
            while self.server.alive:
                try:
                    message = await self.connection.recv()
                    print("Server Recived:")
                    print(message)
                except websockets.exceptions.ConnectionClosed:
                    self.close()
                    return
                header = Message.peekHeader(message)
                if self.name == '':
                    self.name = header['source']
                self.server.routeInternal(header, message)
                self.server.send(header, message)

        def send(self, message):
            asyncio.run_coroutine_threadsafe(self.connection.send(message), self.server.serverThread.loop)

        def close(self):
            self.connection.close()
            self.server.clients.remove(self)