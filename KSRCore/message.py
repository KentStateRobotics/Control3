'''
KentStateRobotics Jared Butcher 7/26/2019

Message Types for structs:

| Format | C-Type             | Python-Type | Size (bytes)                              |
| ------ | ------------------ | ----------- | :---------------------------------------: |
| x      | pad byte           | NA          | 1                                         |
| c      | char               | bytes       | 1                                         |
| b      | signed char        | int         | 1                                         |
| B      | unsigned char      | int         | 1                                         |
| ?      | bool               | bool        | 1                                         |
| h      | short              | int         | 2                                         |
| H      | unsigned short     | int         | 2                                         |
| i      | int                | int         | 4                                         |
| I      | unsigned int       | int         | 4                                         |
| l      | long               | int         | 4                                         |
| L      | unsigned long      | int         | 4                                         |
| q      | long long          | int         | 8                                         |
| Q      | unsigned long long | int         | 8                                         |
| e      | half               | float       | 2                                         |
| f      | float              | float       | 4                                         |
| d      | double             | float       | 8                                         |
| s      | char[]             | bytes       | Fixed size n used as "ns"                 |
| p      | char[]             | bytes       | <= 255 Pascal string sized n used as "np" |
| blob   | char[]             | bytes       | variable                                  |
'''
import struct
from typing import Union
from collections import UserDict
import enum
import json
import logging

MessageLogger = logging.getLogger("Message")

class MessageFactory:
    '''Used to define messages that can be converted to and from bytes for exchange.
        Standared Message Header is automaticly added to the top level of all Messages.
    '''
    _Header = None

    def __init__(self, messageDefinition: dict, includeHeader: bool = True):
        '''`messageDefinition` is a dicitonary of keys and data types as seen above or other `KSRCore.message.MessageFactory`. 
            Use `includeHeader` if no header should be added, used almost exclusively for the `Header` itself.
        '''
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

    def _pack(self, values: dict, topLevel: bool = True) -> bytes:
        '''Packs `values` into bytes according to this's `messageDefinition`.

            `values` is a dictionary of keys and values following the `messageDefinition` to be packed.

            `topLevel` is set to false if no header is to be added at this level
        '''
        topLevel = topLevel and self.includeHeader
        structValues = []
        data = bytes()
        if topLevel:
            data += b's' #Mark as struct as opposed to json
            data += MessageFactory._Header._pack(values['header'], topLevel=False)
        for key in self.structKeys:
            structValues.append(values[key])
        try:
            data += self.struct.pack(*structValues)
        except struct.error as e:
            MessageLogger.error("Error occured while packing: " + str(structValues) + " Into: " + str(self.definition) + " " + str(e))
            print(e)
            raise e
        for key in self.messageKeys:
            data += self.definition[key]._pack(values[key], topLevel=False)
        for key in self.blobKeys:
            data += len(values[key]).to_bytes(4, "big")
            if type(values[key]) == str:
                data += values[key].encode()
            else:
                data += values[key]
        return data

    def _unpack(self, data: bytes, topLevel: bool =True) -> dict:
        '''Unpacks the `data` into a dictionary according to this's `messageDefinition` and returns dictionary of unpacked values, remaining bytes
        '''
        topLevel = topLevel and self.includeHeader
        outDict = self._createDict(topLevel=topLevel)
        if topLevel:
            outDict['header'], data = MessageFactory._Header._unpack(data, topLevel=False)
        structValues = self.struct.unpack_from(data)
        for i in range(len(structValues)):
            outDict[self.structKeys[i]] = structValues[i]
        data = data[self.struct.size:]
        for key in self.messageKeys:
            outDict[key], data = self.definition[key]._unpack(data, topLevel=False)
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
            outDict['header'] = MessageFactory._Header._createDict(topLevel=False)
        return outDict

    def getFormat(self) -> dict:
        '''Returns a copy of this Factory's format dictionary. To be filled and packed.
        '''
        return self.dictFormat.copy()

    def createMessage(self, initalValues: dict = None) -> 'Message':
        '''Create a new instance of `KSRCore.message.Message` from the `messageDefinition`.
            If `initalValues` is given, initalize the message with this dictionary
        '''
        if initalValues is None:
            return Message(self, self.getFormat())
        else:
            return Message(self, initalValues)

    def loads(self, data: Union[str, bytes]) -> 'Message':
        '''Create an instance of `KSRCore.message.Message` from the packed `data`.
            `data` can be either a packed struct or json.
        '''
        if data[0] == ord('s'):
            return Message(self, self._unpack(data[1:])[0])
        elif data[0] == '{':
            return Message(self, json.loads(data))
        else:
            print("Failed to load message data")

class Message(UserDict):
    '''Dictionay for building and manipulating messages
    Do not create directly, use a Message Factory to create
    Values can be added, retereived, or modified using dictionary functions

    The JSON encoding will only accept byte arrays that can be encoded to UTF-8 strings, no raw bytes.
    The JSON encoding is flexable, and does not need to have all entries filled, supportes arrays, dictionaries, 
    and allows aditional fields to be added

    The Struct format will convert strings to byte arrays.
    The Struct format must follow the messageDefinition of the MessageFactory.
    Sub messages can be filled with either a dictionary or a Message object.
    '''
    def __init__(self, factory: MessageFactory, initalValues: dict = {}):
        '''Should not be called directly. Should be called by a `KSRCore.message.MessageFactory`.
        '''
        super().__init__(initalValues)
        self._factory = factory

    class JSONBytesEncoder(json.JSONEncoder):
        '''Json encoder that attempts to encode bytes to str
        '''
        def default(self, obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8')
            if isinstance(obj, Message):
                return obj.data
            return json.JSONEncoder.default(self, obj)

    def toStruct(self) -> bytes:
        '''Packs message into a struct and returns the bytes
        '''
        return self._factory._pack(self)

    def toJson(self) -> str:
        '''Packs message into a json string
        '''
        return json.dumps(self.data, cls=Message.JSONBytesEncoder)

    def setHeader(self, source: int, destination: int, channel: int, messageType: int):
        '''A shortcut for setting header values. All are ints in range 0-255.
        '''
        if 0 > source > 255 or 0 > destination > 255 or 0 > channel > 255 or 0 > messageType > 255:
            raise Exception(f'Incorrect Header values used in setHeader {source} {destination} {channel} {messageType}')
        self['header'] = {}
        self['header']['source'] = source
        self['header']['destination'] = destination
        self['header']['channel'] = channel
        self['header']['type'] = messageType

    @staticmethod
    def setSource(data: Union[bytes, str], source: int) -> Union[bytes, str]:
        '''Change the source of a PREPACKED struct or json message.
        '''
        if data[0] == ord('s'):
            header = justHeaderMessage.loads(data)
            header['header']['source'] = source
            return header.toStruct() + data[6:]
        elif data[0] == '{':
            msg = json.loads(data)
            msg['header']['source'] = source
            return json.dumps(msg, cls=Message.JSONBytesEncoder)

    @staticmethod
    def peekHeader(data: Union[bytes, str]) -> 'Message':
        '''Static function that removes and unpacks a messages header
        '''
        if data[0] == ord('s'):
            return MessageFactory._Header.loads(data)
        elif data[0] == '{':
            return MessageFactory._Header.createMessage(json.loads(data)['header'])

MessageFactory._Header = MessageFactory({
    'source': 'B',
    'destination': 'B',
    'channel': 'B',
    'type': 'B'
}, includeHeader=False)

justHeaderMessage = MessageFactory({})