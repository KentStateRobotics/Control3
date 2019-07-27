import websockets
import threading
import asyncio
from .networkCore import NetworkCore
from .subscriber import Subscriber
from .publisher import Publisher
from .message import Message
from . import messages

class Client(NetworkCore):
    '''Starts a network client. Interface with it as a NetworkCore object
    '''
    def __init__(self, name, port, host=None):
        super().__init__(name, port)
        self.alive = True
        self.host = host
        self.messageQueue = []
        self.subcriberRegistrationPub = Publisher(self, '', Subscriber.REGISTRATION_TOPIC, Message.MessageType.publisher.value, messages.SubscriberMsg)
        self.clientThread = Client.Thread(self)
        self.clientThread.start()

    def send(self, header, message):
        '''Sends message to server
        '''
        if self.isConnected():
            asyncio.run_coroutine_threadsafe(self.clientThread.connection.send(message), self.clientThread.loop)
        else:
            self.messageQueue.append(message)

    def close(self):
        '''Shutdown server, gracefuly?
        '''
        self.alive = False
        asyncio.run_coroutine_threadsafe(self.clientThread.close(), self.clientThread.loop)
        self.clientThread.join()

    def addSubscriber(self, source, topic, messageType, message, callback):
        '''Please use this to create subscribers
        '''
        sub = Subscriber(source, topic, messageType, messageDefinition, callback)
        msg = sub.getRegisterMsg()
        self.subcriberRegistrationPub.publish(msg)
        return sub

    def removeSubscriber(self, subscriber):
        self.subscribers.remove(subscriber)
        msg = subscriber.getRegisterMsg(True)
        self.subcriberRegistrationPub.publish(msg)

    def isConnected(self):
        return not self.clientThread.connection is None and self.clientThread.connection.open

    class Thread(threading.Thread):
        def __init__(self, client):
            self.loop = None
            self.client = client
            self.connection = None
            threading.Thread.__init__(self)
            
        def run(self):
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            while self.client.alive:
                try:
                    self.loop.run_until_complete(self._connectAndRead())
                except (RuntimeError, websockets.exceptions.ConnectionClosed):
                    if self.client.alive:
                        if not self.client.onDisconnect is None:
                            self.client.onDisconnect()
                        print("disconnected, atempting to reconnect")

        async def _connectAndRead(self):
            try:
                async with websockets.connect("ws://" + self.client.host + ":" + str(self.client.port)) as self.connection:
                    print("Connection established")
                    for message in self.client.messageQueue:
                        asyncio.run_coroutine_threadsafe(self.connection.send(message), self.loop)
                    if not self.client.onConnect is None:
                        self.client.onConnect()
                    while self.client.alive:
                        message = await self.connection.recv()
                        print("REC:")
                        print(message)
                        self.client.routeInternal(message.Message.peakHeader(message), message)
            except (ConnectionRefusedError, ConnectionResetError) as e:
                print(e)
                self.client.close()

        async def close(self):
            self.connection.close()
            await self.connection.wait_closed()
            self.loop.stop()