#!/usr/bin/env python
'''
subscriber
KentStateRobotics Jared Butcher 7/21/2019
'''

from . import message, messages
import time

class Subscriber:
    def __init__(self, networkCore, source, topic, messageType, messageDefinition, callback):
        if len(source) > message.NAME_LENGTH or len(topic) > message.NAME_LENGTH:
            raise Exception("Topic or source of subscriber excedied maximum length of {} characters".format(message.NAME_LENGTH))
        self.networkCore = networkCore
        self.messageType = messageType
        self.source = message.padString(source, message.NAME_LENGTH)
        self.topic = message.padString(topic, message.NAME_LENGTH)
        self.messageDefinition = messageDefinition
        self.messagesSent = 0

    def getRegisterMsg(self, remove=False):
        msg = messages.SubscriberMsg.dictFormat
        msg['topic'] = self.topic
        msg['source'] = self.source
        msg['remove'] = remove
        return msg

    def received(self, data):
        self.callback(self.messageDefinition.unpack(data))