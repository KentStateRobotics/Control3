#!/usr/bin/env python
'''
service
KentStateRobotics Jared Butcher 8/28/2019
Implements a service that is started remotely and returns the results (RPC remote procedure call)
'''
from . import networkCore
from .publisher import Publisher
from .message import Message
import time

class Service:
    '''Run on service server
    Runs handle when argumentMessage is received
    '''
    def __init__(self, networkCore, source, topic, argumentMessage, returnMessage, handle):
        self.handle = handle
        self.networkCore = networkCore
        def handleRequest(message):
            self.pub.publish(self.handle(message))

        self.sub = networkCore.addSubscriber(source, topic, Message.MessageType.REQUEST.value, argumentMessage, handleRequest)
        self.pub = Publisher(networkCore, source, topic, Message.MessageType.RESPONSE.value, returnMessage)

    def close(self):
        self.networkCore.removeSubscriber(self.sub)

class ServiceClient:
    '''Used to call the remote service without blocking
    callback is required
    '''
    def __init__(self, networkCore, source, topic, argumentMessage, returnMessage, callback):
        self.networkCore = networkCore
        self.argumentMessage = argumentMessage
        self.sub = networkCore.addSubscriber(source, topic, Message.MessageType.RESPONSE.value, returnMessage, callback)
        self.pub = Publisher(networkCore, source, topic, Message.MessageType.REQUEST.value, argumentMessage)

    def getArgumentFormat(self):
        return self.argumentMessage.getFormat()

    def call(self, arguments):
        '''Call the remote service

        arguments - Filled message format of arguments
        '''
        self.pub.publish(arguments)

    def close(self):
        self.networkCore.removeSubscriber(self.sub)

class ServiceClientBlocking(ServiceClient):
    '''Used to call the remote service, blocking until it returns
    '''
    #Delay between polls
    POLL_INCREMENT = .01

    def __init__(self, networkCore, source, topic, argumentMessage, returnMessage):
        self.receivedMessage = None
        def setReceivedMessage(message):
            self.receivedMessage = message

        super().__init__(networkCore, source, topic, argumentMessage, returnMessage, setReceivedMessage)

    def call(self, arguments, timeout):
        self.receivedMessage = None
        super().call(arguments)
        startTime = time.time()
        while self.receivedMessage is None and startTime - time.time() < timeout:
            time.sleep(ServiceClientBlocking.POLL_INCREMENT)
        if self.receivedMessage is None:
             raise networkCore.TimeoutException("Service failed to resolve before timeout")
        else:
            return self.receivedMessage
