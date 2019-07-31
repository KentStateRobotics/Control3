import websockets
import threading
import asyncio
from .networkCore import NetworkCore
from .subscriber import Subscriber
from .publisher import Publisher
from .message import Message
from .discovery import Discovery
from . import messages
import time

class Client(NetworkCore):
    '''Starts a network client. Interface with it as a NetworkCore object
    '''
    def __init__(self, name, port, host=None, discoveryPort=None, discoveryId=None):
        super().__init__(name, port, discoveryPort)
        self.alive = True
        self.host = host
        self.messageQueue = []
        if not discoveryId is None:
            self.discoveryId = Message.padString(discoveryId, Message.NAME_LENGTH)
        self.subcriberRegistrationPub = Publisher(self, self.name, Subscriber.REGISTRATION_TOPIC, Message.MessageType.publisher.value, messages.SubscriberMsg)
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
        sub = Subscriber(source, topic, messageType, message, callback)
        self.subscribers.append(sub)
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
                except (RuntimeError, websockets.exceptions.ConnectionClosed) as e:
                    if self.client.alive:
                        if not self.client.onDisconnect is None:
                            self.client.onDisconnect()
                        print("disconnected, atempting to reconnect")
                        time.sleep(1)

        async def _connectAndRead(self):
            if self.client.host is None and not self.client.discoveryPort is None:
                self.client.host = Discovery(self.client.discoveryPort).find(self.client.discoveryId, 5)
                if self.client.host == None:
                    print("Failed to find server")
                    self.client.close()
                    return
            try:
                async with websockets.connect("ws://" + self.client.host + ":" + str(self.client.port)) as self.connection:
                    print("Connection established")
                    for message in self.client.messageQueue:
                        asyncio.run_coroutine_threadsafe(self.connection.send(message), self.loop)
                        self.client.messageQueue.remove(message)
                    if not self.client.onConnect is None:
                        self.client.onConnect()
                    while self.client.alive:
                        message = await self.connection.recv()
                        print("REC:")
                        print(message)
                        self.client.routeInternal(Message.peekHeader(message), message)
            except (ConnectionRefusedError, ConnectionResetError) as e:
                print(e)
                self.client.close()

        async def close(self):
            self.connection.close()
            await self.connection.wait_closed()
            self.loop.stop()