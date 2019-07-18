#!/usr/bin/env python
'''
message
KentStateRobotics Jared Butcher 7/17/2019
'''
import struct

class message:
    def __init__(self, name, messageType):
        self.name = name
        self.messageType = messageType
    def pack():
        struct.pack('!10s10s')