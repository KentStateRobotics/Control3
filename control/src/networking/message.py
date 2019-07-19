#!/usr/bin/env python
'''
message
KentStateRobotics Jared Butcher 7/17/2019
'''
import struct
import time

NAME_LENGTH = 10

messageType = {
    publisher: 0,
    request: 1,
    response: 2,
    update: 3
}

class message:
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
                self.messageKeys.append(key)
        self.struct = struct.Struct(self.structFormat)
        self.dictFormat = self._createDict()

    def packMessage(values):
        structValues = []
        for key in self.structKeys:
            if self.messageDefinition[key] == "time":
                structValues.append(time.time())
            else:
                structValues.append(values[key])
        data = self.struct.pack(structValues)
        for key in self.messageKeys:
            data += self.definition[key].packMessage(values[key])
        for key in self.blobKeys:
            data += len(values[key]).to_bytes(4, "big")
            data += values[key]
        return data

    def unpackMessage(data):
        outDict = self._createDict()
        structValues = self.struct.unpack_from(data)
        
        

    def _createDict():
        outDict = {}
        for key,value in self.definition.items():
            if type(value) is str:
                outDict[key] = None
            else:
                outDict[key] = value.getDictionary()
        return outDict

    def getFormat():
        return self.dictFormat

    def __str__(self):
        return self.dictValues.__str__()

    def __repr__(self):
        return self.dictValues.__repr__()