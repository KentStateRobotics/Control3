#!/usr/bin/env python
'''
action
KentStateRobotics Jared Butcher 8/28/2019
An action service. Action is created on a server and Action client is used to start the action.
Status updates are expected to be sent from the server and the server is also expected to send 
the results at the end.
TODO: improve support for multiple clients
'''
from . import networkCore
from .publisher import Publisher
from .message import Message
from enum import Enum
import time

class Action:
    '''Create action and listen for commands. Implementing onCommand is required.
    Command message is to contain a Command
    Status and results are optional
    '''
    def __init__(self, networkCore, source, topic, commandMessge, onCommand, statusMessage=None, resultMessage=None):
        self.commandMessge = commandMessge
        self.statusMessage = statusMessage
        self.resultMessage = resultMessage
        self.commandSub = networkCore.addSubscriber(source, topic, commandMessge, onCommand, messageType=Message.MessageType.REQUEST.value)
        if not statusMessage is None:
            self.statusPub = Publisher(networkCore, topic, statusMessage, messageType=Message.MessageType.STATUS.value)
        if not resultMessage is None:
            self.resultPub = Publisher(networkCore, topic, statusMessage, messageType=Message.MessageType.RESULT.value)

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


class ActionClient:
    '''Use to run and monitor an action
    Command message is to contain a Command
    Status and results are optional
    '''
    def __init__(self, networkCore, source, topic, commandMessge, statusMessage=None, onStatus=None, resultMessage=None, onResult=None):
        self.commandMessge = commandMessge
        self.statusMessage = statusMessage
        self.resultMessage = resultMessage
        self.commandPub = Publisher(networkCore, topic, commandMessge, messageType=Message.MessageType.REQUEST.value)
        self.statusSub = networkCore.addSubscriber(source, topic, statusMessage, onStatus, messageType=Message.MessageType.STATUS.value)
        self.resultSub = networkCore.addSubscriber(source, topic, resultMessage, onResult, messageType=Message.MessageType.RESULT.value)
    
    def getCommandFormat():
        return self.commandMessge.getFormat()

    def sendCommand(commandMessge):
        self.commandPub.publish(commandMessge)