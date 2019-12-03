#!/usr/bin/env python
'''
networking
KentStateRobotics Jared Butcher 7/21/2019
'''
from .message import Message



class NetworkCore:
    def __init__(self, name, port, discoveryPort):
        self.name = Message.padString(name, Message.NAME_LENGTH)
        self.port = port
        self.discoveryPort = discoveryPort
        self.onConnect = None
        self.onDisconnect = None
        self.subscribers = []
        
    def isConnected(self):
        '''Are we connected to the server, defined in child class
        '''
        return False

    def setOnConnect(self, callback):
        self.onConnect = callback

    def setOnDisconnect(self, callback):
        self.onDisconnect = callback

    def send(self, header, data):
        '''Sends bytes to server, defined in child class
        '''
        pass

    def close(self):
        '''Closes the connections and stops any threads, defined in child class
        '''
        pass

    def addSubscriber(self, source, topic, message, callback, messageType=Message.MessageType.PUBLISHER):
        '''Creates and returns a new subscriber, defined in child class
        Refer to the documentaion of Subscriber
        '''
        pass

    def removeSubscriber(self, subscriber):
        '''Removes a subscriber, defined in child class
        '''
        pass

    def routeInternal(self, header, message):
        '''Routes a message among local subscribers

        header - unpacked header of message

        message - bytes of message
        '''
        for sub in self.subscribers:
            sub.received(header, message)

class TimeoutException(Exception):
    def __init__(self, message):
        self.message = message