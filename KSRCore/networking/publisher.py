#!/usr/bin/env python
'''
publisher
KentStateRobotics Jared Butcher 7/26/2019
'''
from .message import Message
import time

class Publisher:
    '''The basic class used for sending data on the network. 
    Publishes a feed under the source, topic, and messageType.

    Args:
        networkCore (NetworkCore): The network core to used to send
        topic (str): Lable the publisher will be publishing under
        messageDefinition (Message) The Message object that received messages are defined by
    Kwargs:
        messageType (Message.MessageType, Optional) The type of this message, used mainly for services and actions
    '''
    def __init__(self, networkCore, topic, messageDefinition, messageType=Message.MessageType.PUBLISHER.value):
        if len(topic) > Message.NAME_LENGTH:
            raise ValueError("Topic of publisher exceaded maximum length of {} characters".format(Message.NAME_LENGTH))
        if type(messageType) != bytes:
            raise TypeError("messageType must be a VALUE of the enum Message.MessageType. Ex: Message.MessageType.PUBLISHER.value")
        self.networkCore = networkCore
        self.messageType = messageType
        self.topic = Message.padString(topic, Message.NAME_LENGTH)
        self.messageDefinition = messageDefinition
        self.sequence = 0

    def publish(self, message):
        '''Sends the message over the network

            message - dict whos format is determined by this publishers Message definiton
        '''
        message['header']['source'] = self.networkCore.name
        message['header']['topic'] = self.topic
        message['header']['timestamp'] = time.time()
        message['header']['sequence'] = self.sequence
        message['header']['messageType'] = self.messageType
        self.sequence += 1
        self.networkCore.send(message['header'], self.messageDefinition.pack(message))