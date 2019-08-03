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
    def __init__(self, networkCore, source, topic, statusMessage, resultMessage, commandMessge, onCommand)
        self.commandSub = networkCore.addSubscriber(source, topic, Message.MessageType.REQUEST.value, commandMessge, onCommand)
        self.statusPub = Publisher(networkCore, source, topic, Message.MessageType.STATUS.value, statusMessage)
        self.resultPub = Publisher(networkCore, source, topic, Message.MessageType.RESULT.value, statusMessage)

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