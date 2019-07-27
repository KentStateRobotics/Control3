#!/usr/bin/env python
'''
message
KentStateRobotics Jared Butcher 7/26/2019
'''
import struct
from enum import Enum

class Message:
    '''Used to define messages that can be converted to and from bytes for exchange

    messageDefinition - a dicitonary of keys and data types or other Messages
    '''

    NAME_LENGTH = 10

    '''Standared Message that is automaticly added to the top level of all Messages, defined at bottom of file
    '''
    Header = None

    def __init__(self, messageDefinition, includeHeader=True):
        self.definition = messageDefinition
        self.structFormat = "!"
        self.includeHeader = includeHeader
        self.structKeys = []
        self.messageKeys = []
        self.blobKeys = []
        for key,value in messageDefinition.items():
            if type(value) is str:
                if value == "blob":
                    self.blobKeys.append(key)
                else:
                    self.structKeys.append(key)
                    self.structFormat += value
            else:
                self.messageKeys.append(key)
        self.struct = struct.Struct(self.structFormat)
        self.dictFormat = self._createDict()

    def pack(self, values, topLevel=True):
        '''Returns bytes of the dictionary values packed according to this Messages definition

        topLevel - if True include a header
        '''
        topLevel = topLevel and self.includeHeader
        structValues = []
        data = bytes()
        if topLevel:
            data += Message.Header.pack(values['header'], topLevel=False)
        for key in self.structKeys:
            structValues.append(values[key])
        data += self.struct.pack(*structValues)
        for key in self.messageKeys:
            data += self.definition[key].pack(values[key], topLevel=False)
        for key in self.blobKeys:
            data += len(values[key]).to_bytes(4, "big")
            data += values[key]
        return data

    def unpack(self, data, topLevel=True):
        '''Unpacks the bytes into a dictionary according to this Messages definition.
        Returns dictionary of unpacked values, remaining bytes

        data - bytes to unpack

        topLevel - does this level have a header
        '''
        topLevel = topLevel and self.includeHeader
        outDict = self._createDict(topLevel=topLevel)
        if topLevel:
            outDict['header'], data = Message.Header.unpack(data, topLevel=False)
        structValues = self.struct.unpack_from(data)
        for i in range(len(structValues)):
            outDict[self.structKeys[i]] = structValues[i]
        data = data[self.struct.size:]
        for key in self.messageKeys:
            outDict[key], data = self.definition[key].unpack(data, topLevel=False)
        for key in self.blobKeys:
            size = int.from_bytes(data[:4], "big")
            data = data[4:]
            outDict[key] = data[:size]
            data = data[size:]
        return outDict, data

    def _createDict(self, topLevel=True):
        '''Internal function to generate an empty format dictionary
        '''
        topLevel = topLevel and self.includeHeader
        outDict = {}
        for key,value in self.definition.items():
            if type(value) is str:
                outDict[key] = None
            else:
                outDict[key] = value._createDict(topLevel=False)
        if topLevel:
            outDict['header'] = Message.Header._createDict(topLevel=False)
        return outDict

    def getFormat(self):
        '''Returns a copy of this Messages format dictionary. To be filled and packed.
        '''
        return self.dictFormat.copy()

    def peekHeader(data):
        '''Static function that removes and unpacks a messages header
        '''
        header, data = Message.Header.unpack(data, topLevel=False)
        return header

    def padString(value, length):
        '''Static function that takes a string or bytes and either pads or truncates it to the length

        returns bytes
        '''
        if type(value) == str:
            value = value.encode()
        adjValue = value[:length]
        adjValue += b'\x00' * (length - len(adjValue))
        return adjValue

    class MessageType(Enum):
        '''Used in header to define what type of message is being published under the topic
        '''
        publisher = b'\x00'
        request = b'\x01'
        response = b'\x02'
        update = b'\x03'


Message.Header = Message({
    'timestamp': 'f',
    'source': str(Message.NAME_LENGTH) + 's',
    'topic': str(Message.NAME_LENGTH) + 's',
    'messageType': 'c',
    'sequence': 'I'
}, includeHeader=False)