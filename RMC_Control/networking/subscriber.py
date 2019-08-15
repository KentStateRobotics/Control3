#!/usr/bin/env python
'''
subscriber
KentStateRobotics Jared Butcher 7/26/2019
'''
from .message import Message
from . import messages
import time

class Subscriber:
    '''The basic class used for receiving data from the network. 
    Subscribes to the feeds of publishers with matching source, topic, and messageType.

    source - Name of the sending network core

    topic - Lable the publisher will be publishing under

    messageType - The Message.MessageType this subscriber is listening for, must be a char

    messageDefinition - The Message object that received messages are defined by

    callback - f(message) - A function to call with the unpacked message when one is received
    '''
    REGISTRATION_TOPIC='subReg'

    def __init__(self, source, topic, messageType, messageDefinition, callback):
        if len(topic) > Message.NAME_LENGTH:
            raise ValueError("Topic of subscriber excedied maximum length of {} characters".format(Message.NAME_LENGTH))
        if type(messageType) != bytes:
            raise TypeError("messageType must be a VALUE of the enum Message.MessageType. Ex: Message.MessageType.PUBLISHER.value")
        self.messageType = messageType
        self.source = Message.padString(source, Message.NAME_LENGTH)
        self.topic = Message.padString(topic, Message.NAME_LENGTH)
        self.messageDefinition = messageDefinition
        self.callback = callback

    def getRegisterMsg(self, remove=False):
        '''Generate the message used to register or unregister this subscriber. Returns a SubscriberMsg dictionary
        '''
        msg = messages.SubscriberMsg.dictFormat
        msg['topic'] = self.topic
        msg['source'] = self.source
        msg['messageType'] = self.messageType
        msg['remove'] = remove
        return msg

    def topicMatch(self, header):
        '''Does this subscriber subscribe to this message
        '''
        return (self.source == Message.padString('', Message.NAME_LENGTH) or self.source == header['source']) and self.topic == header['topic'] and self.messageType == header['messageType']

    def registrationMatch(registration, header):
        '''Static does this subscriber registration discribe and subscriber that listens for this message
        '''
        return ((registration['source'] == Message.padString('', Message.NAME_LENGTH) or registration['source'] == header['source']) and registration['topic'] == header['topic'] 
        and registration['messageType'] == header['messageType'])

    def received(self, header, data):
        '''If this subscriber subscrives to the given message then it will be sent
        '''
        if self.topicMatch(header):
            self.callback(self.messageDefinition.unpack(data)[0])