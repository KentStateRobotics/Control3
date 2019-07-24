#!/usr/bin/env python
'''
networking
KentStateRobotics Jared Butcher 7/21/2019
'''
import websockets
import threading
import struct
import socket
import asyncio
from . import message, publisher, subscriber, messages

REGISTRATION_TOPIC = ''

class NetworkCore:
    def __init__(self, name, port, host=None):
        self.running = True
        if len(name) > message.NAME_LENGTH:
            raise Exception("Name has exceded maximum length of {} characters".format(message.NAME_LENGTH))
        self.name = message.padString(name, message.NAME_LENGTH)
        self.host = host
        self.port = port
        self.alive = True
        self.publishers = []
        self.subscribers = []
        if host is None:
            self.clients = []
            self.registrationSub = self.subscriber('', REGISTRATION_TOPIC, messages.SubscriberMsg, self._hostRegisterSub)
        else:
            self.registrationPub = self.publisher(REGISTRATION_TOPIC, messages.SubscriberMsg)
            self.sendQueue = []
        self.thread = NetworkThread(self)
        self.thread.start()

    def destory(self):
        print("DESTORY CORE")
        self.alive = False
        for client in self.clients:
            client.destory()
        if not self.thread is None:
            self.thread.alive = False
            if not self.thread.loop is None:
                self.thread.loop.call_soon_threadsafe(self.thread.loop.stop)
            self.thread.join()

    def publisher(self, topic, messageDefinition):
        pub = publisher.Publisher(self, self.name, topic, message.MessageType.publisher.value, messageDefinition)
        self.publishers.append(pub)
        return pub

    def subscriber(self, source, topic, messageDefinition, callback):
        sub = subscriber.Subscriber(self, source, topic, message.MessageType.publisher.value, messageDefinition, callback)
        self.subscribers.append(sub)
        if not self.host is None:
            self.registrationPub.publish(sub.getRegisterMsg())
        return sub

    def removeSubscriber(self, subscriber):
        self.subscribers.remove(subscriber)
        self.registrationPub.publish(subscriber.getRegisterMsg(True))

    def _hostRegisterSub(self, subMsg):
        for client in self.clients:
            if client.name == subMsg['header']['source']:
                if subMsg['remove']:
                    for sub in client.subs:
                        if sub['topic'] == subMsg['topic'] and sub['source'] == subMsg['source'] and sub['messageType'] == subMsg['messageType']:
                            client.subs.remove(sub)
                else:
                    client.subs.append(subMsg)

    def isConnectedToServer(self):
        return not self.thread.conn is None

    def routeMessageLocal(self, header, message):
        for sub in self.subscribers:
            if (sub.source == '' or sub.source == header['source']) and sub.topic == header['topic'] and sub.messageType == header['messageType']:
                sub.received(message)

    def routeMessageExternal(self, header, message):
        if self.host is None:
            for client in self.clients:
                for sub in client.subs:
                    if (sub['source'] == '' or sub['source'] == header['source']) and sub['topic'] == header['topic'] and sub['messageType'] == header['messageType']:
                        client.send(message)
                        break
        else:
            if self.isConnectedToServer():
                self.thread.clientSendToServer(message)
            else:
                self.sendQueue.append(message)

    def onConnect(self):
        for message in self.sendQueue:
            self.thread.clientSendToServer(message)
            self.sendQueue.remove(message)

class NetworkClient:
    def __init__(self, core, conn):
        self.core = core
        self.conn = conn
        self.name = ''
        self.alive = True
        self.subs = []
        self.loop = asyncio.get_event_loop()

    async def read(self):
        while self.alive:
            try:
                message = await self.conn.recv()
                print("REC:")
                print(message)
            except websockets.exceptions.ConnectionClosed:
                self.destory()
                return
            header = message.Message.peakHeader(message)
            if self.name == '':
                self.name = header['source']
            self.core.routeMessageExternal(header, message)
            self.core.routeMessageLocal(header, message)

    def send(self, message):
        asyncio.run_coroutine_threadsafe(self.conn.send(message), self.loop)

    def destory(self):
        self.alive = False
        self.subs = None
        self.core.clients.remove(self)

class NetworkThread(threading.Thread):
    def __init__(self, core):
        self.alive = True
        self.core = core
        self.loop = None
        if not self.core.host is None:
            self.conn = None
        threading.Thread.__init__(self)

    def run(self):
        print("Networking thread started")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        if self.core.host is None:
            self.server = self.loop.run_until_complete(websockets.server.serve(self._recNewConn, host='', port=self.core.port, loop=self.loop))
        else:
            self.uri = "ws://" + self.core.host + ":" + str(self.core.port)
            while self.alive:
                try:
                    self.loop.run_until_complete(self._clientConnectAndRead())
                except websockets.exceptions.ConnectionClosed:
                    self.conn = None
                    print("disconnected, atempting to reconnect")
        self.loop.run_forever()

    async def _recNewConn(self, conn, url):
        print("Received new Connection Request")
        client = NetworkClient(self.core, conn)
        self.core.clients.append(client)
        await client.read()
    
    async def _clientConnectAndRead(self):
        try:
            async with websockets.connect(self.uri) as self.conn:
                print("Connection established")
                self.core.onConnect()
                while self.alive:
                    message = await self.conn.recv()
                    print("REC:")
                    print(message)
                    self.core.routeMessageLocal(message.Message.peakHeader(message), message)
        except (ConnectionRefusedError, ConnectionResetError) as e:
            self.conn = None
            print(e)
            return

    def clientSendToServer(self, message):
        try:
            asyncio.run_coroutine_threadsafe(self.conn.send(message), self.loop)
        except (ConnectionRefusedError, ConnectionResetError) as e:
            print(e)
            return
    
    def _stopAndReconnect(self):
        self.loop.stop()
        self.loop.run_until_complete(self._clientConnectAndRead())
        self.loop.run_forever()
