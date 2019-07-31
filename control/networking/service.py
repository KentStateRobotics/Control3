#!/usr/bin/env python
'''
service
KentStateRobotics Jared Butcher 7/31/2019
'''
from . import networkCore
from .publisher import Publisher
from .message import Message
import time

class Service:
    def __init__(self, networkCore, source, topic, argumentMessage, returnMessage, handle):
        self.handle = handle
        self.networkCore = networkCore
        def handleRequest(message):
            self.pub.publish(self.handle(message))

        self.sub = networkCore.addSubscriber(source, topic, Message.MessageType.request.value, argumentMessage, handleRequest)
        self.pub = Publisher(networkCore, source, topic, Message.MessageType.response.value, returnMessage)

    def close(self):
        self.networkCore.removeSubscriber(self.sub)

class ProxyService:
    def __init__(self, networkCore, source, topic, argumentMessage, returnMessage, callback):
        self.networkCore = networkCore
        self.sub = networkCore.addSubscriber(source, topic, Message.MessageType.response.value, returnMessage, callback)
        self.pub = Publisher(networkCore, source, topic, Message.MessageType.request.value, argumentMessage)

    def call(self, arguments):
        self.pub.publish(arguments)

    def close(self):
        self.networkCore.removeSubscriber(self.sub)

class ProxyServiceBlocking(ProxyService):

    POLL_INCREMENT = .01

    def __init__(self, networkCore, source, topic, argumentMessage, returnMessage):
        self.receivedMessage = None
        def setReceivedMessage(message):
            self.receivedMessage = message

        super().__init__(networkCore, source, topic, argumentMessage, returnMessage, setReceivedMessage)

    def call(self, arguments, timeout):
        super().call(arguments)
        startTime = time.time()
        while self.receivedMessage is None and startTime - time.time() < timeout:
            time.sleep(POLL_INCREMENT)
        if self.receivedMessage is None:
             raise networkCore.TimeoutException("Service failed to resolve before timeout")
        else:
            return self.receivedMessage
