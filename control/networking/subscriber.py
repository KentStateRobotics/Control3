#!/usr/bin/env python
'''
subscriber
KentStateRobotics Jared Butcher 7/21/2019
'''

from . import message, messages
import time

class Subscriber:
    def __init__(self, networkCore, messageType, source, topic, message, callback):
        if len(source) > message.NAME_LENGTH or len(topic) > message.NAME_LENGTH:
            raise Exception("Topic or source of subscriber excedied maximum length of {} characters".format(message.NAME_LENGTH))
        self.networkCore = networkCore
        self.messageType = messageType
        self.source = padString(source, message.NAME_LENGTH)
        self.topic = padString(topic, message.NAME_LENGTH)
        self.message = message
        self.messagesSent = 0

    def getRegisterMsg(self, remove=False):
        msg = messages.SubscriberMsg.dictFormat
        msg['topic'] = self.topic
        msg['source'] = self.source
        msg['remove'] = remove
        return msg

    def received(self, data):
        self.callback(self.message.unpack(data))