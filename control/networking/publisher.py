#!/usr/bin/env python
'''
publisher
KentStateRobotics Jared Butcher 7/21/2019
'''
from . import message
import time

class Publisher:
    def __init__(self, networkCore, source, topic, messageType, messageDefinition):
        if len(source) > message.NAME_LENGTH or len(topic) > message.NAME_LENGTH:
            raise Exception("Topic or source of publisher exceaded maximum length of {} characters".format(message.NAME_LENGTH))
        self.networkCore = networkCore
        self.messageType = messageType
        self.source = message.padString(source, message.NAME_LENGTH)
        self.topic = message.padString(topic, message.NAME_LENGTH)
        self.messageDefinition = messageDefinition
        self.sequence = 0

    def publish(self, message):
        message['header']['source'] = self.networkCore.name
        message['header']['topic'] = self.topic
        message['header']['timestamp'] = time.time()
        message['header']['sequence'] = self.sequence
        message['header']['messageType'] = self.messageType
        self.networkCore.routeMessageExternal(message['header'], self.messageDefinition.pack(message))

    