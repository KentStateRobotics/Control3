#!/usr/bin/env python
'''
message
KentStateRobotics Jared Butcher 7/17/2019
'''
import struct
import time
from enum import Enum

NAME_LENGTH = 10

class MessageType(Enum):
    publisher = b'\x00'
    request = b'\x01'
    response = b'\x02'
    update = b'\x03'

Header = None


def padString(value, length):
    return value[:length].ljust(length, '\x00')

class Message:
    def __init__(self, messageDefinition):
        self.definition = messageDefinition
        self.structFormat = "!"
        self.structKeys = []
        self.messageKeys = []
        self.blobKeys = []
        for key,value in messageDefinition.items():
            if type(value) is str:
                if value == "time":
                    self.structKeys.append(key)
                    self.structFormat += "f"
                elif value == "blob":
                    self.blobKeys.append(key)
                else:
                    self.structKeys.append(key)
                    self.structFormat += value
            else:
                self.messageKeys.append(key)
        self.struct = struct.Struct(self.structFormat)
        self.dictFormat = self._createDict()

    def pack(self, values, topLevel=True):
        structValues = []
        for key in self.structKeys:
            if self.definition[key] == "time":
                structValues.append(time.time())
            else:
                structValues.append(values[key])
        data = self.struct.pack(*structValues)
        if topLevel:
            data += Header.pack(values['header'], topLevel=False)
        for key in self.messageKeys:
            data += self.definition[key].pack(values[key], topLevel=False)
        for key in self.blobKeys:
            data += len(values[key]).to_bytes(4, "big")
            data += values[key]
        return data

    def unpack(self, data, topLevel=True):
        outDict = self._createDict(topLevel=topLevel)
        structValues = self.struct.unpack_from(data)
        for i in range(len(structValues)):
            outDict[self.structKeys[i]] = structValues[i]
        data = data[self.struct.size:]
        if topLevel:
            outDict['header'], data = Header.unpack(data, topLevel=False)
        for key in self.messageKeys:
            outDict[key], data = self.definition[key].unpack(data, topLevel=False)
        for key in self.blobKeys:
            size = int.from_bytes(data[:4], "big")
            data = data[4:]
            outDict[key] = data[:size]
            data = data[size:]
        return outDict, data

    def _createDict(self, topLevel=True):
        outDict = {}
        for key,value in self.definition.items():
            if type(value) is str:
                outDict[key] = None
            else:
                outDict[key] = value._createDict(topLevel=False)
        if topLevel and not Header is None:
            outDict['header'] = Header._createDict(topLevel=False)
        return outDict

    def getFormat(self):
        return self.dictFormat

Header = Message({
    'timeStamp': 'time',
    'sender': str(NAME_LENGTH) + 's',
    'topic': str(NAME_LENGTH) + 's',
    'messageType': 'c',
    'sequence': 'I'
})