#!/usr/bin/env python
'''
action
KentStateRobotics Jared Butcher 7/31/2019
'''
from . import networkCore
from .publisher import Publisher
from .message import Message
import time

class Action:
    def __init__(self, networkCore, source, topic, commandMessge, onCommand, statusMessage=None, resultMessage=None)
        self.commandMessge = commandMessge
        self.statusMessage = statusMessage
        self.resultMessage = resultMessage
        self.commandSub = networkCore.addSubscriber(source, topic, Message.MessageType.REQUEST.value, commandMessge, onCommand)
        if not statusMessage is None:
            self.statusPub = Publisher(networkCore, source, topic, Message.MessageType.STATUS.value, statusMessage)
        if not resultMessage is None:
            self.resultPub = Publisher(networkCore, source, topic, Message.MessageType.RESULT.value, statusMessage)

    def getStatusFormat():
        if self.statusMessage is None:
            raise ValueError("This action does not define a status message")
        else:
            return self.statusMessage.getFormat()

    def getResultFormat():
        if self.statusMessage is None:
            raise ValueError("This action does not define a result message")
        else:
            return self.statusMessage.getFormat()

    def sendStatus(statusMessage):
        if self.statusMessage is None:
            raise ValueError("This action does not define a status message")
        else:
            self.statusPub.publish(statusMessage)

    def sendResult(resultMessage):
        if self.statusMessage is None:
            raise ValueError("This action does not define a result message")
        else:
            self.resultPub.publish(resultMessage)

    class Command(Enum):
        '''Used command messages
        '''
        START = b'\x00' #Cancles previous commands and starts this one
        ENQUEUE = b'\x01' #Adds command to queue
        CLEAR = b'\x02' #Cancles all commands
        SKIP = b'\x03' #Cancles current command

CommandBase = Message({
    'command' = b'c'
})

class ActionClient:
    def __init__(self, networkCore, source, topic, commandMessge, statusMessage=None, onStatus=None, resultMessage=None, onResult=None):
        self.commandMessge = commandMessge
        self.statusMessage = statusMessage
        self.resultMessage = resultMessage
        self.commandPub = Publisher(networkCore, source, topic, Message.MessageType.REQUEST.value, commandMessge)
        self.statusSub = networkCore.addSubscriber(source, topic, Message.MessageType.STATUS.value, statusMessage, onStatus)
        self.resultSub = networkCore.addSubscriber(source, topic, Message.MessageType.RESULT.value, resultMessage, onResult)
    
    def getCommandFormat():
        return self.commandMessge.getFormat()

    def sendCommand(commandMessge):
        self.commandPub.publish(commandMessge)